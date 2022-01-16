"""Add social table

Revision ID: f3fb4be1bf60
Revises: 954621c0c962
Create Date: 2022-01-16 18:59:13.458090

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f3fb4be1bf60"
down_revision = "954621c0c962"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "social",
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.Column("page_count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organization.id"],
            name=op.f("fk_social_organization_id_organization"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_social")),
    )
    op.create_index(
        op.f("ix_social_organization_id"), "social", ["organization_id"], unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_social_organization_id"), table_name="social")
    op.drop_table("social")
