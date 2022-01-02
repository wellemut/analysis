"""Store webpage content in database

Revision ID: 800c6503e3c0
Revises: 7dd8f628eba5
Create Date: 2022-01-01 20:17:34.820512

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "800c6503e3c0"
down_revision = "7dd8f628eba5"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("webpage", sa.Column("content", sa.String(), nullable=True))
    op.drop_column("webpage", "file_name")


def downgrade():
    op.add_column(
        "webpage",
        sa.Column("file_name", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.drop_column("webpage", "content")
