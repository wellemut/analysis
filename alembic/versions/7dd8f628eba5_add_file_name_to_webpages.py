"""Add file name to webpages

Revision ID: 7dd8f628eba5
Revises: fb0dc271187b
Create Date: 2021-12-27 20:40:41.851896

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7dd8f628eba5"
down_revision = "fb0dc271187b"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("webpage", sa.Column("file_name", sa.String(), nullable=True))


def downgrade():
    op.drop_column("webpage", "file_name")
