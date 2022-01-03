"""Add language to text blocks

Revision ID: aba304e0839b
Revises: ca1c093c56b3
Create Date: 2022-01-03 20:26:03.740109

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "aba304e0839b"
down_revision = "ca1c093c56b3"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("textblock", sa.Column("language", sa.String(), nullable=True))


def downgrade():
    op.drop_column("textblock", "language")
