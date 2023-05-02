"""empty message

Revision ID: 04eaff9bcc55
Revises: 
Create Date: 2023-04-10 12:56:26.377798

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '04eaff9bcc55'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("tests", "risk", new_column_name="score")
    pass


def downgrade() -> None:
    op.alter_column("tests", "score", new_column_name="risk")
    pass