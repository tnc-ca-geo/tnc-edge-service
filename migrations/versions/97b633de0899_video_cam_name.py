"""video_cam_name

Revision ID: 97b633de0899
Revises: 81b92a299311
Create Date: 2023-07-27 15:50:13.450935

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '97b633de0899'
down_revision = '81b92a299311'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('video_files', sa.Column('cam_name', sa.VARCHAR(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('video_files', 'cam_name')
    # ### end Alembic commands ###
