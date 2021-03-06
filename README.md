# Getting Started

## Installation

Set up Python 3.8 with `pipenv`. After cloning this repository, run `pipenv install` to set up the virtual environment and install all required dependencies. All Python commands mentioned below should be run inside the pipenv shell (activate with `pipenv shell`).

## Environment variables

Copy `.env.sample` to `.env` and fill in the required API keys.

## Setting up the databases

Run `python setup.py` to set up the SQLite databases needed and seed them with an initial list of organizations.

## Performing the analysis

To run the analysis, just start `python run.py`. It automatically starts one pipeline after the other, beginning with web scraping, moving on to keyword matching, and then to metadata collection. All pipelines are listed in the `pipelines` directory.

# Notes

## Scraping Organizations' Facebook profiles

Facebook has a wealth of valuable information about organizations on their profile pages, including:

- name (`name`)
- profile picture (edge: `picture`)
- location (`contact_address`, `current_location`, `location`, and `single_line_address`)
- email address (`emails`)
- phone number (`phone`)
- twitter URL (edge: `screennames`) [reference](https://developers.facebook.com/docs/graph-api/reference/v9.0/page/screennames)
- short description (`about` and `mission`)
- long description (`company_overview`, `description`, and `general_info`)
- category (non-profit vs for-profit) (`category`)
- founding year (`founded`)

See the API reference for the Page API: https://developers.facebook.com/docs/graph-api/reference/page

The endpoint requires knowledge of the page's ID. This can be retrieved via the
`/{page_id_or_username}` endpoint.

However, none of this information can be accessed without the `Page Public Metadata Access` feature.
Getting access to this feature requires evidence of official business
registration/incorporation documents. This process is described in detail
here: https://www.facebook.com/business/help/159334372093366?locale=en_US

## Scraping Organizations' LinkedIn profiles

LinkedIn has a very restrictive API when it comes to public business profiles.

The following information is available:

- name (`name` and `localizedName`)
- logo (`logoV2`)
- location (`locations`)

See the API reference for the Organization Lookup API: https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/organizations/organization-lookup-api

This information can only be accessed once LinkedIn has granted access to its
Marketing Developer Platform. The creation process seems straightforward:
Create a public LinkedIn page (e.g., Global Goals Directory) and then follow
the instructions listed here: https://docs.microsoft.com/en-us/linkedin/marketing/getting-started#how-do-i-access-marketing-apis
