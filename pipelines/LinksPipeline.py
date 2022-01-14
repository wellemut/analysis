from models import Link, Website, Webpage
from helpers import extract_links_from_html, get_domain_from_url


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
                    target_domain = cls.get_target_domain(link)

                    # Only process links that are web links, email addresses, or
                    # phone numbers
                    if not cls.is_web_or_email_or_phone(link):
                        continue

                    # Exclude any internal links
                    if target_domain == domain:
                        continue

                    # If we have no target domain, just save link as is
                    if target_domain is None:
                        Link.create(source_webpage_id=webpage.id, target=link)
                        continue

                    # Otherwise, find or create target website...
                    if target_domain not in domain_to_website_id_map:
                        target_website = Website.find_by_or_create(domain=target_domain)
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
    def get_target_domain(cls, url):
        return get_domain_from_url(url) if cls.is_web(url) else None

    @classmethod
    def is_web_or_email_or_phone(cls, url):
        url = url.lower()
        return cls.is_web(url) or url.startswith("mailto:") or url.startswith("tel:")

    @classmethod
    def is_web(cls, url):
        url = url.lower()
        return url.startswith("https://") or url.startswith("http://")