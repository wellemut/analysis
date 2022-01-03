"""Add text blocks

Revision ID: ca1c093c56b3
Revises: 800c6503e3c0
Create Date: 2022-01-02 21:40:36.057811

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ca1c093c56b3"
down_revision = "800c6503e3c0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "textblock",
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hash", sa.String(), nullable=False),
        sa.Column("word_count", sa.Integer(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_textblock")),
    )
    op.create_index(op.f("ix_textblock_hash"), "textblock", ["hash"], unique=True)
    op.create_table(
        "webpagetextblock",
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("webpage_id", sa.Integer(), nullable=False),
        sa.Column("text_block_id", sa.Integer(), nullable=False),
        sa.Column("tag", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["text_block_id"],
            ["textblock.id"],
            name=op.f("fk_webpagetextblock_text_block_id_textblock"),
        ),
        sa.ForeignKeyConstraint(
            ["webpage_id"],
            ["webpage.id"],
            name=op.f("fk_webpagetextblock_webpage_id_webpage"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_webpagetextblock")),
    )
    op.create_index(
        op.f("ix_webpagetextblock_text_block_id"),
        "webpagetextblock",
        ["text_block_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_webpagetextblock_webpage_id"),
        "webpagetextblock",
        ["webpage_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(op.f("ix_webpagetextblock_webpage_id"), table_name="webpagetextblock")
    op.drop_index(
        op.f("ix_webpagetextblock_text_block_id"), table_name="webpagetextblock"
    )
    op.drop_table("webpagetextblock")
    op.drop_index(op.f("ix_textblock_hash"), table_name="textblock")
    op.drop_table("textblock")
