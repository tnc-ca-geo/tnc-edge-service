"""add_timezones

Revision ID: 1d1b10e054af
Revises: 58dd42108a22
Create Date: 2023-07-12 14:59:24.746444

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d1b10e054af'
down_revision = '58dd42108a22'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('ALTER TABLE boatschedules ALTER COLUMN datetime TYPE timestamp with time zone;')
    op.execute('ALTER TABLE deckhandevents ALTER COLUMN datetime TYPE timestamp with time zone;')
    op.execute('ALTER TABLE fishaidata ALTER COLUMN datetime TYPE timestamp with time zone;')
    op.execute('ALTER TABLE gpsdata ALTER COLUMN datetime TYPE timestamp with time zone;')
    op.execute('ALTER TABLE internetdata ALTER COLUMN datetime TYPE timestamp with time zone;')
    op.execute('ALTER TABLE ondeckdata ALTER COLUMN datetime TYPE timestamp with time zone;')
    op.execute('ALTER TABLE tests ALTER COLUMN datetime TYPE timestamp with time zone;')
    # op.execute('ALTER TABLE tests ALTER COLUMN datetime_from TYPE timestamp with time zone;')
    # op.execute('ALTER TABLE tests ALTER COLUMN datetime_to TYPE timestamp with time zone;')
    # op.execute('ALTER TABLE video_files ALTER COLUMN last_modified TYPE timestamp with time zone;')
    # op.execute('ALTER TABLE video_files ALTER COLUMN decrypted_datetime TYPE timestamp with time zone;')
    # pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('ALTER TABLE boatschedules ALTER COLUMN datetime TYPE timestamp without time zone;')
    op.execute('ALTER TABLE deckhandevents ALTER COLUMN datetime TYPE timestamp without time zone;')
    op.execute('ALTER TABLE fishaidata ALTER COLUMN datetime TYPE timestamp without time zone;')
    op.execute('ALTER TABLE gpsdata ALTER COLUMN datetime TYPE timestamp without time zone;')
    op.execute('ALTER TABLE internetdata ALTER COLUMN datetime TYPE timestamp without time zone;')
    op.execute('ALTER TABLE ondeckdata ALTER COLUMN datetime TYPE timestamp without time zone;')
    op.execute('ALTER TABLE tests ALTER COLUMN datetime TYPE timestamp without time zone;')
    # ### end Alembic commands ###
