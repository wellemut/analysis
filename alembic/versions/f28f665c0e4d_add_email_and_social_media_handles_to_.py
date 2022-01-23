"""Add email and social media handles to organization

Revision ID: f28f665c0e4d
Revises: f3fb4be1bf60
Create Date: 2022-01-20 19:59:51.475138

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f28f665c0e4d"
down_revision = "f3fb4be1bf60"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "organization", sa.Column("email_address", sa.String(), nullable=True)
    )
    op.add_column(
        "organization", sa.Column("facebook_handle", sa.String(), nullable=True)
    )
    op.add_column(
        "organization", sa.Column("twitter_handle", sa.String(), nullable=True)
    )
    op.add_column(
        "organization", sa.Column("linkedin_handle", sa.String(), nullable=True)
    )


def downgrade():
    op.drop_column("organization", "linkedin_handle")
    op.drop_column("organization", "twitter_handle")
    op.drop_column("organization", "facebook_handle")
    op.drop_column("organization", "email_address")
