"""Add organization table

Revision ID: b2d423b0748b
Revises: becf86db12ce
Create Date: 2022-01-15 11:06:58.131706

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "b2d423b0748b"
down_revision = "becf86db12ce"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "organization",
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("website_id", sa.Integer(), nullable=False),
        sa.Column("homepage", sa.String(), nullable=True),
        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(
            ["website_id"],
            ["website.id"],
            name=op.f("fk_organization_website_id_website"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_organization")),
    )
    op.create_index(
        op.f("ix_organization_website_id"), "organization", ["website_id"], unique=True
    )


def downgrade():
    op.drop_index(op.f("ix_organization_website_id"), table_name="organization")
    op.drop_table("organization")
