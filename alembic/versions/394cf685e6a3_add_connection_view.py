"""Add connection view

Revision ID: 394cf685e6a3
Revises: a567578eb6e1
Create Date: 2022-01-15 15:10:33.145592

"""
from alembic import op
import sqlalchemy as sa
from alembic_utils.pg_view import PGView
from sqlalchemy import text as sql_text

# revision identifiers, used by Alembic.
revision = "394cf685e6a3"
down_revision = "a567578eb6e1"
branch_labels = None
depends_on = None


def upgrade():
    public_connection = PGView(
        schema="public",
        signature="connection",
        definition="SELECT source_organization.id AS source_organization_id, source_website.domain AS source_domain, target_organization.id AS target_organization_id, target_website.domain AS target_domain, count(link.id) AS link_count \nFROM link JOIN webpage AS source_webpage ON source_webpage.id = link.source_webpage_id JOIN website AS source_website ON source_website.id = source_webpage.website_id JOIN organization AS source_organization ON source_website.id = source_organization.website_id JOIN webpage AS target_webpage ON target_webpage.id = link.target_webpage_id JOIN website AS target_website ON target_website.id = target_webpage.website_id JOIN organization AS target_organization ON target_website.id = target_organization.website_id GROUP BY source_organization.id, source_website.domain, target_organization.id, target_website.domain ORDER BY source_organization.id, target_organization.id",
    )
    op.create_entity(public_connection)


def downgrade():
    public_connection = PGView(
        schema="public",
        signature="connection",
        definition="SELECT source_organization.id AS source_organization_id, source_website.domain AS source_domain, target_organization.id AS target_organization_id, target_website.domain AS target_domain, count(link.id) AS link_count \nFROM link JOIN webpage AS source_webpage ON source_webpage.id = link.source_webpage_id JOIN website AS source_website ON source_website.id = source_webpage.website_id JOIN organization AS source_organization ON source_website.id = source_organization.website_id JOIN webpage AS target_webpage ON target_webpage.id = link.target_webpage_id JOIN website AS target_website ON target_website.id = target_webpage.website_id JOIN organization AS target_organization ON target_website.id = target_organization.website_id GROUP BY source_organization.id, source_website.domain, target_organization.id, target_website.domain ORDER BY source_organization.id, target_organization.id",
    )
    op.drop_entity(public_connection)
