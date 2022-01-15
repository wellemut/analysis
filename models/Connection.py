from sqlalchemy.sql import func
from sqlalchemy.orm import aliased, relationship
from models import BaseView, Link, Organization, Webpage, Website

target_organization = aliased(Organization, name="target_organization")
target_website = aliased(Website, name="target_website")
target_webpage = aliased(Webpage, name="target_webpage")

source_organization = aliased(Organization, name="source_organization")
source_website = aliased(Website, name="source_website")
source_webpage = aliased(Webpage, name="source_webpage")


class Connection(BaseView):
    __view_query__ = (
        Link.query.join(source_webpage, Link.source_webpage)
        .join(source_website, source_webpage.website)
        .join(source_organization, source_website.organization)
        .join(target_webpage, Link.target_webpage)
        .join(target_website, target_webpage.website)
        .join(target_organization, target_website.organization)
        .with_entities(
            source_organization.id.label("source_organization_id"),
            source_website.domain.label("source_domain"),
            target_organization.id.label("target_organization_id"),
            target_website.domain.label("target_domain"),
            func.count(Link.id).label("link_count"),
        )
        .group_by(
            source_organization.id,
            source_website.domain,
            target_organization.id,
            target_website.domain,
        )
        .order_by(source_organization.id, target_organization.id)
    )

    source_organization = relationship(
        "Organization",
        backref="outbound_connections",
        primaryjoin=(
            "foreign(Connection.source_organization_id) == remote(Organization.id)"
        ),
        uselist=False,
        viewonly=True,
    )
    target_organization = relationship(
        "Organization",
        backref="inbound_connections",
        primaryjoin=(
            "foreign(Connection.target_organization_id) == remote(Organization.id)"
        ),
        uselist=False,
        viewonly=True,
    )
