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
    EXTRACTORS = dict(
        email_address=EmailExtractor,
        facebook_handle=FacebookExtractor,
        twitter_handle=TwitterExtractor,
        linkedin_handle=LinkedinExtractor,
    )

    @classmethod
    def process(cls, domain):
        print(f"Identifying socials for {domain}:", end=" ")

        # Count the number of webpages that belong to this domain
        website = Website.find_by(domain=domain)
        organization = website.organization
        number_of_scraped_pages = Webpage.query.filter_by(
            website=website, is_ok_and_has_content=True
        ).count()

        # Set up extractor instances
        extractors = []
        for column, Extractor in cls.EXTRACTORS.items():
            extractor = Extractor(domain=domain, page_count=number_of_scraped_pages)
            extractor.name = column
            extractors.append(extractor)

        # Top level domains to filter for
        top_level_domains = set()
        for extractor in extractors:
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
                        Link.id,
                        Link.source_webpage_id,
                        Website.top_level_domain,
                        func.coalesce(Link.target, Webpage.url).label("target"),
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
                        extractor.process(
                            link=link.target,
                            link_id=link.id,
                            page_id=link.source_webpage_id,
                        )

                # Print progress indicator
                print(".", end="")

        for extractor in extractors:
            organization.fill(**{extractor.name: extractor.top_candidate})
            for handle, page_count in extractor.counts.items():
                Social.create(
                    organization_id=organization.id,
                    type=extractor.name,
                    value=handle,
                    page_count=page_count,
                )
        organization.save()

        print("")
        print(
            "Identified",
            Social.query.filter_by(organization=website.organization).count(),
            "socials",
        )
