"""second

Revision ID: f835aa8c569a
Revises: 04eaff9bcc55
Create Date: 2023-05-16 11:44:58.986312

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f835aa8c569a'
down_revision = '04eaff9bcc55'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('boatschedules',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sentence', sa.String(), nullable=True),
    sa.Column('datetime', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('deckhandevents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('jsonblob', sa.String(), nullable=True),
    sa.Column('datetime', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('fishaidata',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('video_uri', sa.String(), nullable=True),
    sa.Column('cocoannotations_uri', sa.String(), nullable=True),
    sa.Column('datetime', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('gpsdata',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sentence', sa.String(), nullable=True),
    sa.Column('datetime', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('internetdata',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('traceroute', sa.String(), nullable=True),
    sa.Column('ping', sa.Float(), nullable=True),
    sa.Column('packetloss', sa.Float(), nullable=True),
    sa.Column('returncode', sa.Integer(), nullable=True),
    sa.Column('datetime', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('vectors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('configblob', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('type', sa.Enum('one', 'two', 'three', name='t'), nullable=True),
    sa.Column('vector_id', sa.Integer(), nullable=True),
    sa.Column('score', sa.Float(), nullable=True),
    sa.Column('detail', sa.String(), nullable=True),
    sa.Column('datetime', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['vector_id'], ['vectors.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tests')
    op.drop_table('vectors')
    op.drop_table('internetdata')
    op.drop_table('gpsdata')
    op.drop_table('fishaidata')
    op.drop_table('deckhandevents')
    op.drop_table('boatschedules')
    # ### end Alembic commands ###