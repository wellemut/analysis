"""Add homepage to website

Revision ID: f6674722bf85
Revises: cf5380b356f1
Create Date: 2022-01-12 20:24:22.909448

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f6674722bf85"
down_revision = "cf5380b356f1"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("website", sa.Column("homepage", sa.String(), nullable=True))


def downgrade():
    op.drop_column("website", "homepage")
