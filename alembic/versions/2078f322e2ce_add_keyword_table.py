"""Add keyword table

Revision ID: 2078f322e2ce
Revises: 4a001236925c
Create Date: 2022-01-06 11:14:43.185227

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2078f322e2ce"
down_revision = "4a001236925c"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "keyword",
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("text_block_id", sa.Integer(), nullable=False),
        sa.Column("keyword", sa.String(), nullable=False),
        sa.Column("sdg", sa.Integer(), nullable=False),
        sa.Column("start", sa.Integer(), nullable=False),
        sa.Column("end", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["text_block_id"],
            ["textblock.id"],
            name=op.f("fk_keyword_text_block_id_textblock"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_keyword")),
    )
    op.create_index(
        op.f("ix_keyword_text_block_id"), "keyword", ["text_block_id"], unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_keyword_text_block_id"), table_name="keyword")
    op.drop_table("keyword")
