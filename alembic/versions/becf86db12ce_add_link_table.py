"""Add link table

Revision ID: becf86db12ce
Revises: f6674722bf85
Create Date: 2022-01-14 17:30:36.742547

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "becf86db12ce"
down_revision = "f6674722bf85"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "link",
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_webpage_id", sa.Integer(), nullable=False),
        sa.Column("target_webpage_id", sa.Integer(), nullable=True),
        sa.Column("target", sa.String(), nullable=True),
        sa.CheckConstraint(
            "(target_webpage_id IS NULL) <> (target IS NULL)",
            name=op.f("ck_link_target_webpage_id_xor_target"),
        ),
        sa.ForeignKeyConstraint(
            ["source_webpage_id"],
            ["webpage.id"],
            name=op.f("fk_link_source_webpage_id_webpage"),
        ),
        sa.ForeignKeyConstraint(
            ["target_webpage_id"],
            ["webpage.id"],
            name=op.f("fk_link_target_webpage_id_webpage"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_link")),
    )
    op.create_index(
        op.f("ix_link_source_webpage_id"), "link", ["source_webpage_id"], unique=False
    )
    op.create_index(
        op.f("ix_link_target_webpage_id"), "link", ["target_webpage_id"], unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_link_target_webpage_id"), table_name="link")
    op.drop_index(op.f("ix_link_source_webpage_id"), table_name="link")
    op.drop_table("link")
