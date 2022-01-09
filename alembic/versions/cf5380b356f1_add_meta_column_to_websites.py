"""Add meta column to websites

Revision ID: cf5380b356f1
Revises: e9232f3e04cc
Create Date: 2022-01-09 20:34:33.716089

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cf5380b356f1"
down_revision = "e9232f3e04cc"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("website", sa.Column("meta", sa.JSON(), nullable=True))


def downgrade():
    op.drop_column("website", "meta")
