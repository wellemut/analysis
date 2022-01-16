from models import Link, Website, Webpage
from helpers import (
    extract_links_from_html,
    get_domain_from_url,
    get_top_level_domain_from_url,
)


class LinksPipeline:
    @classmethod
    def process(cls, domain):
        print(f"Collecting links for {domain}:", end=" ")

        # Get IDs for all webpages that belong to this domain and that have
        # content and status code 200
        website = Website.find_by(domain=domain)
        webpage_ids = Webpage.query.filter_by(
            website=website, is_ok_and_has_content=True
        ).ids()

        # Cache domains and urls to their corresponding record IDs
        domain_to_website_id_map = dict()
        url_to_webpage_id_map = dict()

        with website.session.begin():
            # Clear existing links
            Link.delete_by_website(website)

            # For each page, ...
            for id in webpage_ids:
                webpage = Webpage.find(id)

                # ... extract links from HTML content
                for link in extract_links_from_html(webpage.content):
                    # If we have an email address or a phone number, save link
                    # as is
                    if cls.is_email(link) or cls.is_phone(link):
                        Link.create(source_webpage_id=webpage.id, target=link)
                        continue

                    target_domain = get_domain_from_url(link)

                    # If we have no target domain, the URL does not start with
                    # http(s) or is malformed.
                    # If the target domain is equal to the current domain, we
                    # have an internal link.
                    # In both cases, we ignore the link and move on
                    if target_domain is None or target_domain == domain:
                        continue

                    # Otherwise, find or create target website...
                    if target_domain not in domain_to_website_id_map:
                        target_website = Website.find_by_or_create(
                            domain=target_domain,
                            top_level_domain=get_top_level_domain_from_url(link),
                        )
                        domain_to_website_id_map[target_domain] = target_website.id

                    # ... and target webpage
                    if link not in url_to_webpage_id_map:
                        website_id = domain_to_website_id_map[target_domain]
                        params = dict(website_id=website_id, url=link)
                        target_webpage_id = (
                            Webpage.id.query.filter_by(**params).scalar()
                            or Webpage.create(**params).id
                        )
                        url_to_webpage_id_map[link] = target_webpage_id

                    Link.create(
                        source_webpage_id=webpage.id,
                        target_webpage_id=url_to_webpage_id_map[link],
                    )

                # Print progress indicator
                print(".", end="")

        # Print summary stats
        print("")
        print(
            "Extracted",
            Link.query.join(Link.source_webpage)
            .where(Webpage.website == website)
            .count(),
            "links",
        )

    @classmethod
    def is_email(cls, url):
        return url.lower().startswith("mailto:") and "@" in url

    @classmethod
    def is_phone(cls, url):
        return url.lower().startswith("tel:")
