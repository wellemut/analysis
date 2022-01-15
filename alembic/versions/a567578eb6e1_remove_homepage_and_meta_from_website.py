"""Remove homepage and meta from website

Revision ID: a567578eb6e1
Revises: b2d423b0748b
Create Date: 2022-01-15 11:18:06.511114

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a567578eb6e1"
down_revision = "b2d423b0748b"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("website", "meta")
    op.drop_column("website", "homepage")


def downgrade():
    op.add_column(
        "website",
        sa.Column("homepage", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "website",
        sa.Column(
            "meta",
            postgresql.JSON(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
    )
