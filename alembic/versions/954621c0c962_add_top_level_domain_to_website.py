"""Add top level domain to website

Revision ID: 954621c0c962
Revises: 394cf685e6a3
Create Date: 2022-01-15 19:13:33.397980

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "954621c0c962"
down_revision = "394cf685e6a3"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("website", sa.Column("top_level_domain", sa.String(), nullable=False))
    op.create_index(
        op.f("ix_website_top_level_domain"),
        "website",
        ["top_level_domain"],
        unique=False,
    )


def downgrade():
    op.drop_index(op.f("ix_website_top_level_domain"), table_name="website")
    op.drop_column("website", "top_level_domain")
