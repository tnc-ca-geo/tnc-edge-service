"""new boatschedule table

Revision ID: 1d99d3d6427d
Revises: 90960f3ecc5e
Create Date: 2023-04-10 17:29:16.360235

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d99d3d6427d'
down_revision = '90960f3ecc5e'
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
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('boatschedules')
    # ### end Alembic commands ###