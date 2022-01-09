"""Add status, headers, and mime to webpage

Revision ID: e9232f3e04cc
Revises: 2078f322e2ce
Create Date: 2022-01-09 08:13:43.363291

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e9232f3e04cc"
down_revision = "2078f322e2ce"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("webpage", sa.Column("status_code", sa.Integer(), nullable=True))
    op.add_column("webpage", sa.Column("headers", sa.String(), nullable=True))
    op.add_column("webpage", sa.Column("mime_type", sa.String(), nullable=True))


def downgrade():
    op.drop_column("webpage", "mime_type")
    op.drop_column("webpage", "headers")
    op.drop_column("webpage", "status_code")
