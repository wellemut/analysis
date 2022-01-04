"""Make text block website-scoped (add website ID to text blocks)

Revision ID: 4a001236925c
Revises: aba304e0839b
Create Date: 2022-01-03 22:22:34.975379

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4a001236925c"
down_revision = "aba304e0839b"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("textblock", sa.Column("website_id", sa.Integer(), nullable=False))
    op.drop_index("ix_textblock_hash", table_name="textblock")
    op.create_unique_constraint(
        op.f("uq_textblock_website_id"), "textblock", ["website_id", "hash"]
    )
    op.create_foreign_key(
        op.f("fk_textblock_website_id_website"),
        "textblock",
        "website",
        ["website_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint(
        op.f("fk_textblock_website_id_website"), "textblock", type_="foreignkey"
    )
    op.drop_constraint(op.f("uq_textblock_website_id"), "textblock", type_="unique")
    op.create_index("ix_textblock_hash", "textblock", ["hash"], unique=True)
    op.drop_column("textblock", "website_id")
