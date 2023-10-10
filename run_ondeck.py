
from datetime import datetime, timezone
import click
import json
import os
from pathlib import Path
import re
import requests
from requests import Response
import schedule
import subprocess
from subprocess import CompletedProcess
import time

from model import Base as ModelBase, VideoFile, OndeckData
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker as SessionMaker, Query
from sqlalchemy.orm.session import Session

from flask.config import Config as FlaskConfig
flaskconfig = FlaskConfig(root_path='')

flaskconfig.from_object('config.defaults')
if 'ENVIRONMENT' in os.environ:
    flaskconfig.from_envvar('ENVIRONMENT')

def next_videos(session: Session, thalos_cam_name):
     workday_start_hour_at_utc_interval = '8 hours';
     workday_start_hour_at_utc_timestr = '08:00Z';
     num_vids_required = 4;
     results: Query[VideoFile] = session.query(VideoFile).from_statement(sa.text(
        """
        select video_files.* from video_files 
        join (
            select COALESCE(max(workday_counts.workday), '1970-01-01') most_recent_active_workday 
            from (
                select date(start_datetime AT TIME ZONE 'utc' - interval :timei ) as workday,
                    count(*) as count 
                from video_files 
                where decrypted_path is not null 
                group by workday
            ) workday_counts 
            where workday_counts.count > :numvids
        ) workdays 
        on video_files.start_datetime >= workdays.most_recent_active_workday + time with time zone :times 
        left join ondeckdata 
        on video_files.decrypted_path = ondeckdata.video_uri 
        where video_files.decrypted_path is not null 
        and ondeckdata.video_uri is null
        and video_files.cam_name = :cam_name
        order by video_files.decrypted_datetime asc;
        """)).params(
         {
             "timei": workday_start_hour_at_utc_interval,
             "times": workday_start_hour_at_utc_timestr,
             "numvids": num_vids_required,
             "cam_name": thalos_cam_name,
         })
     return list(results)

MAGIC_VALUE_5_MiB = 5 * 1024 * 1024

def run_ondeck(output_dir: Path, engine: Path, sessionmaker: SessionMaker, thalos_cam_name):
    
    video_files: list[VideoFile] = []

    with sessionmaker() as session:
        video_files = next_videos(session, thalos_cam_name)

    # click.echo(video_files)
    while len(video_files) > 0:
        video_file: VideoFile = video_files.pop(0)
        # click.echo(video_file)
        decrypted_path = Path(video_file.decrypted_path)
        last_dot_index: int = decrypted_path.name.index('.')
        if last_dot_index < 0:
            last_dot_index = None
        json_out_file: Path = output_dir / Path(decrypted_path.name[0:last_dot_index] + "_ondeck.json")

        ondeck_input = str(decrypted_path.absolute())
        try:
            reencoded_path: Path = Path(video_file.reencoded_path)
            if reencoded_path.stat().st_size > MAGIC_VALUE_5_MiB:
                ondeck_input = str(reencoded_path.absolute())
        except:
            pass

        # sudo /usr/bin/docker run --rm -v /videos:/videos --runtime=nvidia --network none gcr.io/edge-gcr/edge-service-image:latest --output /videos --input /videos/21-07-2023-09-55.avi
        cmd: str = "sudo /usr/bin/docker run --rm -v /videos:/videos --runtime=nvidia --network none \
                gcr.io/edge-gcr/edge-service-image:latest \
                --output %s --input %s"%(
            str(json_out_file.absolute()), 
            ondeck_input
            )
        if engine:
            cmd += " --model %s"%( str(engine.absolute()), )
        p: CompletedProcess[str] = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if p.returncode == 0:

            parse_json(sessionmaker, decrypted_path, json_out_file)
        else:
            # click.echo("ondeck model failure. stdout, stderr: {} {}".format( p.stdout, p.stderr))
            with sessionmaker() as session:
                session.execute(sa.text("insert into ondeckdata ( video_uri, cocoannotations_uri ) \
                            values ( :decrypted_path, :error_str ) ;"), {
                                "decrypted_path": str(decrypted_path.absolute()),
                                "error_str": "ondeck model failure. stdout, stderr: " + p.stdout + p.stderr
                        }
                )
                session.commit()
        with sessionmaker() as session:
            video_files = next_videos(session, thalos_cam_name)

def parse_json(sessionmaker, decrypted_path, json_out_file):
    with json_out_file.open() as f:
        o: dict = json.load(f)
        cnt = o.get('overallCount')
        runtime = o.get('overallRuntimeMs')
        frames = o.get('frames', [])

                ## stats
        trackedframes = filter(lambda frame: len(frame.get('trackingIds'))>0, frames)
        confidencesarrs = map(lambda frame: frame.get('confidence'), trackedframes)
        confidences = [c for confidencesarr in confidencesarrs for c in confidencesarr]
        if len(confidences) > 0:
            meanconf = float(sum(confidences)) / float(len(confidences))
        else:
            meanconf = 0

                ## tracks
        tracks = {}
        for f in frames:
            frame_confidences = f.get('confidence')
            i = 0
            for trackid in f.get('trackingIds'):
                if trackid not in tracks:
                    t = {
                                "first_frame": f.get('frameNum'),
                                "first_timestamp": f.get('timestamp'),
                                "confidences": []
                            }
                    tracks[trackid] = t
                t = tracks[trackid]
                if len(frame_confidences) > i:
                    t['confidences'].append(frame_confidences[i])
                else:
                    t['confidences'].append(0)
                i += 1
                        

        with sessionmaker() as session:
            session.execute(sa.text("insert into ondeckdata ( video_uri, cocoannotations_uri, \
                                            overallcount, overallruntimems, tracked_confidence ) \
                                values ( :decrypted_path, :json_out_file , :cnt, :runt, :mean_c) ;"), {
                                    "decrypted_path": str(decrypted_path.absolute()),
                                    "json_out_file":str(json_out_file.absolute()),
                                    "cnt":cnt, 
                                    "runt":runtime, 
                                    "mean_c":meanconf,
                            }
                    )
            session.commit()


def v2_enqueue(output_dir: Path, sessionmaker: SessionMaker, thalos_cam_name: str):
    
    video_files: list[VideoFile] = []

    with sessionmaker() as session:
        video_files = next_videos(session, thalos_cam_name)

        # print(video_files)
        while len(video_files) > 0:
            video_file: VideoFile = video_files.pop(0)
            # print(video_file)
            decrypted_path = Path(video_file.decrypted_path)
            last_dot_index: int = decrypted_path.name.index('.')
            if last_dot_index < 0:
                last_dot_index = None
            json_out_file: Path = output_dir / Path(decrypted_path.name[0:last_dot_index] + "_ondeck.json")

            ondeck_input = str(decrypted_path.absolute())
            try:
                reencoded_path: Path = Path(video_file.reencoded_path)
                if reencoded_path.stat().st_size > MAGIC_VALUE_5_MiB:
                    ondeck_input = str(reencoded_path.absolute())
            except:
                pass

            try:
                r: Response = requests.post('http://127.0.0.1:5000/inference', json={
                    "input_path":ondeck_input, 
                    "output_path":str(json_out_file.absolute()),
                    "current_timestamp": video_file.start_datetime.astimezone(timezone.utc).replace(tzinfo=None).isoformat() +  ".00Z"
                })

                click.echo("resp: {} body: {}".format(repr(r), repr(r.json())))

                with sessionmaker() as session:
                    session.execute(sa.text("""insert into ondeckdata ( video_uri, cocoannotations_uri, status )
                                values ( :ondeck_input, :ondeck_output, :status )
                                on conflict DO UPDATE SET status = :status ;"""), {
                                    "ondeck_input": ondeck_input,
                                    "ondeck_output": str(json_out_file.absolute()),
                                    "status": "queued"
                            }
                    )
                    session.commit()
            except requests.exceptions.RequestException as e:
                click.echo("ondeck model request exception: {}".format(e))
                return

MAGIC_VALUE_1_MINUTE = 60

def v2_parse(output_dir: Path, sessionmaker: SessionMaker):
    # only pick files that end with _ondeck.json
    a = filter(lambda x: x.is_file() and x.name.endswith('_ondeck.json'), output_dir.iterdir())

    epoch_now = int(time.time())
    # only pick files that haven't been modified in the last minute
    b = filter(lambda x: x.stat().st_mtime + MAGIC_VALUE_1_MINUTE < epoch_now, a)

    # get the filenames
    c = map(lambda x: str(x.absolute()) , b)

    found_ondeck_files = list(c)

    with sessionmaker() as session:
        results: Query[OndeckData] = session.query(OndeckData).where(OndeckData.status == 'queued')
        for pending_ondeckdata in results:
            if pending_ondeckdata.video_uri in found_ondeck_files:
                pending_ondeckdata.status = "parsing"
                session.commit()
                


def v2_errors(sessionmaker: SessionMaker):
    try:
        r: Response = requests.get('http://127.0.0.1:5000/errors')

        click.echo("errors resp: {} body: {}".format(repr(r), repr(r.json())))

        for error in r:
            input_path = r.get('input_path')
            error_message = r.get('error_message')

            with sessionmaker() as session:
                session.execute(sa.text("insert into ondeckdata ( video_uri, cocoannotations_uri ) \
                            values ( :decrypted_path, :error_str ) ;"), {
                                "decrypted_path": input_path,
                                "error_str": "ondeck model failure. stdout, stderr: " + error_message
                        }
                )
                session.commit()

    except requests.exceptions.RequestException as e:
        click.echo("ondeck model errors request exception: {}".format(e))
        return

@click.command()
@click.option('--dbname', default=flaskconfig.get('DBNAME'))
@click.option('--dbuser', default=flaskconfig.get('DBUSER'))
@click.option('--output_dir', default=flaskconfig.get('VIDEO_OUTPUT_DIR'))
@click.option('--engine', default=flaskconfig.get('ONDECK_MODEL_ENGINE'))
@click.option('--thalos_cam_name', default=flaskconfig.get('THALOS_CAM_NAME'))
@click.option('--print_queue', is_flag=True)
@click.option('--parsetesta')
@click.option('--parsetestb')
@click.option('--force_v2', is_flag=True)
def main(dbname, dbuser, output_dir, engine, thalos_cam_name, print_queue, parsetesta, parsetestb, force_v2: bool):

    output_dir = Path(output_dir)

    if engine:
        engine = Path(engine)


    sa_engine = sa.create_engine("postgresql+psycopg2://%s@/%s"%(dbuser, dbname), echo=True)
    sessionmaker = SessionMaker(sa_engine)

    ModelBase.metadata.create_all(sa_engine)

    if parsetesta and parsetestb:
        parse_json(sessionmaker, Path(parsetesta), Path(parsetestb))
        return

    if print_queue:
        with sessionmaker() as session:
            video_files = next_videos(session, thalos_cam_name)
            for v in video_files:
                click.echo(v.decrypted_path)
        return

    use_v2 = False
    try:
        r: Response = requests.get('http://127.0.0.1:5000/queueSummary')
        use_v2 = r.status_code == 200
        click.echo("resp: {} body: {}".format(repr(r), repr(r.json())))
    except requests.exceptions.RequestException as e:
        click.echo("ondeck model request exception: {}".format(e))

    if force_v2 or use_v2:
        
        def runonce(output_dir, sessionmaker, thalos_cam_name):
            v2_enqueue(output_dir, sessionmaker, thalos_cam_name)
            return schedule.CancelJob
        
        schedule.every(1).seconds.do(runonce, output_dir, sessionmaker, thalos_cam_name)

        schedule.every(5).minutes.do(v2_enqueue, output_dir, sessionmaker, thalos_cam_name )
    else:

        def runonce(output_dir, engine, sessionmaker, thalos_cam_name):
            run_ondeck(output_dir, engine, sessionmaker, thalos_cam_name)
            return schedule.CancelJob
        
        schedule.every(1).seconds.do(runonce, output_dir, engine, sessionmaker, thalos_cam_name)

        schedule.every(5).minutes.do(run_ondeck, output_dir, engine, sessionmaker, thalos_cam_name )

    while 1:
        n = schedule.idle_seconds()
        if n is None:
            # no more jobs
            break
        elif n > 0:
            # sleep exactly the right amount of time
            click.echo("sleeping for: {}".format(n))
            time.sleep(n)
        schedule.run_pending()

if __name__ == '__main__':
    main()

