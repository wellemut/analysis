from sqlalchemy import or_
from sqlalchemy.sql import func
from models import Link, Social, Webpage, Website
from helpers import batches
from helpers.extractors import (
    EmailExtractor,
    FacebookExtractor,
    LinkedinExtractor,
    TwitterExtractor,
)


class SocialsPipeline:
    EXTRACTORS = [
        FacebookExtractor,
        TwitterExtractor,
        LinkedinExtractor,
        EmailExtractor,
    ]

    @classmethod
    def process(cls, domain):
        print(f"Identifying socials for {domain}:", end=" ")

        website = Website.find_by(domain=domain)

        # Set up extractor instances
        extractors = [Extractor() for Extractor in cls.EXTRACTORS]

        # Top level domains to filter for
        top_level_domains = set()
        for extractor in cls.EXTRACTORS:
            top_level_domains.update(extractor.top_level_domains)

        # Check if top level domains include None
        query_conditions = []
        if None in top_level_domains:
            query_conditions.append(Website.top_level_domain == None)
            top_level_domains.remove(None)

        # Check if any other top level domains remain
        if len(top_level_domains) > 0:
            query_conditions.append(Website.top_level_domain.in_(top_level_domains))

        # Get IDs for all links that belong to this domain and that point to one
        # of the relevant top level domains
        link_ids = (
            Link.query.with_transformation(Link.with_filter_by_source_website(website))
            .join(Link.target_webpage, isouter=True)
            .join(Webpage.website, isouter=True)
            .where(or_(False, *query_conditions))
            .order_by(Link.id)
            .ids()
        )

        with website.session.begin():
            Social.delete_by_website(website)

            # Process links in batches of 100 each
            for ids in batches(link_ids, 100):
                links = (
                    Link.query.join(Link.target_webpage, isouter=True)
                    .join(Webpage.website, isouter=True)
                    .where(Link.id.in_(ids))
                    .with_entities(
                        func.coalesce(Link.target, Webpage.url).label("target"),
                        Website.top_level_domain,
                        Link.source_webpage_id,
                    )
                    .all()
                )

                # For each link, ...
                for link in links:
                    # ... identify the relevant extractor based on top level domain
                    for extractor in extractors:
                        if link.top_level_domain not in extractor.top_level_domains:
                            continue

                        # ...and extract the value (handle, email address, ...)
                        extractor.process(link=link.target, page=link.source_webpage_id)

                # Print progress indicator
                print(".", end="")

        for extractor in extractors:
            for handle, page_count in extractor.counts.items():
                Social.create(
                    organization_id=website.organization.id,
                    type=extractor.name,
                    value=handle,
                    page_count=page_count,
                )

        print("")
        print(
            "Identified",
            Social.query.filter_by(organization=website.organization).count(),
            "socials",
        )
