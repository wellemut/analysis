from helpers.extractors import BaseExtractor, LinkedinExtractor


def test_it_is_an_extractor():
    assert issubclass(LinkedinExtractor, BaseExtractor)


def test_it_extracts_valid_handles():
    links = {
        "https://www.linkedin.com/company/organisation-eco-cooperation-development-organisation-cooperation-developpement-eco/jobs/": "organisation-eco-cooperation-development-organisation-cooperation-developpement-eco",
        "https://www.linkedin.com/company/interface/": "interface",
        "https://www.linkedin.com/company/fundaci%C3%B3n-futuro-latinoamericano/": "fundaci%c3%b3n-futuro-latinoamericano",
        "https://www.linkedin.com/company/33193187/admin/": "33193187",
        "https://linkedin.com/company/ipcc": "ipcc",
        "https://www.linkedin.com/school/12668": "12668",
        "https://www.linkedin.com/school/berlinprofessionalschool-hwrberlin/": "berlinprofessionalschool-hwrberlin",
        "https://www.linkedin.com/showcase/henkel-beauty-care/": "henkel-beauty-care",
    }
    for url, handle in links.items():
        assert (url, LinkedinExtractor.extract(url)) == (url, handle)


def test_it_ignores_links_without_valid_handle():
    links = [
        "https://in.linkedin.com/in/subratasingh",
        "http://linkedin.com/",
        "https://www.linkedin.com/business/talent/blog/talent-strategy/leaders-most-popular-courses-hr-great-reshuffle",
        "https://socialimpact.linkedin.com/environmental-sustainability",
        "https://www.linkedin.com/sharing/share-offsite/?url=https://smallarmssurvey.org/database/global-firearms-holdings",
        "https://www.linkedin.com/feed/news/jeffrey-sachs-taking-your-questions-4950332/",
        "https://www.linkedin.com/groups/1245687/profile",
        "https://www.linkedin.com/legal/cookie-policy",
        "https://www.linkedin.com/jobs/view/1723467118/",
    ]
    for url in links:
        assert (url, LinkedinExtractor.extract(url)) == (url, None)