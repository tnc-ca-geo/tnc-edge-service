"""vector_schedulestring

Revision ID: 47ff3fca73a4
Revises: 5e4898954923
Create Date: 2023-06-06 13:07:09.704169

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '47ff3fca73a4'
down_revision = '5e4898954923'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('vectors', sa.Column('schedule_string', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('vectors', 'schedule_string')
    # ### end Alembic commands ###