"""create website and webpage

Revision ID: fb0dc271187b
Revises: 
Create Date: 2021-12-19 08:19:17.689270

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fb0dc271187b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "website",
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("domain", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_website")),
    )
    op.create_index(op.f("ix_website_domain"), "website", ["domain"], unique=True)
    op.create_table(
        "webpage",
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("website_id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("depth", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["website_id"], ["website.id"], name=op.f("fk_webpage_website_id_website")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_webpage")),
        sa.UniqueConstraint("url", name=op.f("uq_webpage_url")),
    )
    op.create_index(
        op.f("ix_webpage_website_id"), "webpage", ["website_id"], unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_webpage_website_id"), table_name="webpage")
    op.drop_table("webpage")
    op.drop_index(op.f("ix_website_domain"), table_name="website")
    op.drop_table("website")
