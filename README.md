# globalgoals.directory: analysis

This repo contains the code for mapping organizations to the 17 Sustainable
Development Goals using natural language processing (NLP).

> ⚠ Work in progress: This is a complete rebuild of the analyis pipelines, built
> for Docker, backed by PostgreSQL, fully tested, and with a massively expanded
> and improved set of SDG keywords. The rebuild is not yet complete. For the
> discontinued stable version, see the `v1` branch.

## Table of Contents

- [globalgoals.directory: analysis](#globalgoalsdirectory-analysis)
  - [Table of Contents](#table-of-contents)
  - [Deployment](#deployment)
    - [Creating VPS](#creating-vps)
    - [Configuring Dokku](#configuring-dokku)
    - [Upgrading Dokku](#upgrading-dokku)
    - [Creating the application](#creating-the-application)
    - [Creating the database](#creating-the-database)
    - [Setting environment variables](#setting-environment-variables)
    - [Deploying the application](#deploying-the-application)
    - [Enabling HTTPS](#enabling-https)
  - [Running one-off tasks](#running-one-off-tasks)
  - [Development](#development)
    - [Hot Reloading](#hot-reloading)
    - [Managing dependencies](#managing-dependencies)
    - [Managing migrations](#managing-migrations)
    - [Accessing the database](#accessing-the-database)
    - [Backing up the database](#backing-up-the-database)
  - [Testing](#testing)
  - [Scraping](#scraping)
  - [References](#references)
    - [Language Detection](#language-detection)
    - [SDG Keywords](#sdg-keywords)

## Deployment

### Creating VPS

The code is deployed on DigitalOcean (1 GB VPS), using the Dokku image from the
marketplace.

### Configuring Dokku

After setting up the droplet, make sure to set up Dokku by going to the droplet
IP address and filling in the hostname: `api.globalgoals.directory`

We may need to double check the hostname. We can check the hostname using:

```
$ dokku domains:report --global
       Domains global enabled:        true
       Domains global vhosts:         api.globalgoals.directory
```

If this does not return `api.globalgoals.directory`, we need to set it manually:

```
$ dokku domains:set-global api.globalgoals.directory
```

### Upgrading Dokku

Then, we updated Dokku to the
[latest version](https://github.com/dokku/dokku/releases) by installing system
updates:

```
$ sudo apt update
$ sudo apt upgrade
$ sudo reboot
```

Now `dokku --version` should return the latest version.

### Creating the application

Switch to the `dokku` user.

```
$ su dokku
$ cd /
```

Create the application:

```
$ dokku apps:create analysis
-----> Creating analysis...
```

Initialize a bare git repo (which will serve as a remote for deployment):

```
$ dokku git:initialize analysis
-----> Initializing git repository for analysis
```

We also need to enable Docker Buildkit support (for caching dependencies
between builds for faster deployments):

```
$ echo "export DOCKER_BUILDKIT=1" | sudo tee -a /etc/default/dokku
$ echo "export BUILDKIT_PROGRESS=plain" | sudo tee -a /etc/default/dokku
```

### Creating the database

Install the postgres plugin (from `root`!):

```
$ sudo dokku plugin:install https://github.com/dokku/dokku-postgres.git
```

Set up the postgres container:

```
$ dokku postgres:create analysisdb
$ dokku postgres:link analysisdb analysis
```

This automatically creates the `DATABASE_URL` env var in Dokku, but we need to
replace the adapter from `postgres` to `postgresql` for use with SQLAlchemy:

```
$ dokku config:get analysis DATABASE_URL
postgres://<user>:<password>@<hostname>:5432/analysisdb
$ dokku config:set analysis DATABASE_URL=postgresql://...
```

### Setting environment variables

**NOTE: Currently, the project uses no environment variables (other than the ones set via `dokku`).**

To import environment variables from `.env` to Dokku, run the following command:

```
$ grep -v '^#' .env | xargs -d '\n' ssh dokku@api.globalgoals.directory config:set analysis
-----> Setting config vars
       VAR1:  abc
       VAR2:  def
-----> Restarting app analysis
-----> Releasing analysis...
```

### Deploying the application

**On your local machine**, add the new git remote and push:

```
$ git remote add dokku dokku@api.globalgoals.directory:analysis
$ git push dokku main
Enumerating objects: 36, done.
Counting objects: 100% (36/36), done.
Delta compression using up to 8 threads
Compressing objects: 100% (22/22), done.
Writing objects: 100% (36/36), 2.87 KiB | 489.00 KiB/s, done.
Total 36 (delta 11), reused 0 (delta 0)
-----> Cleaning up...
-----> Building analysis from dockerfile...
remote: build context to Docker daemon   7.68kB
Step 1/5 : FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
python3.7: Pulling from tiangolo/uvicorn-gunicorn-fastapi

...lots more output

-----> Attempting pre-flight checks (web.1)
   Waiting for 10 seconds ...
   Default container check successful!
-----> Running post-deploy
-----> Creating new app virtual host file...
-----> Configuring api.globalgoals.directory...(using built-in template)
-----> Creating http nginx.conf
       Reloading nginx
-----> Renaming containers
       Renaming container (4a2bb8363848) to analysis.web.1
=====> Application deployed:
       http://api.globalgoals.directory
```

Visit [http://api.globalgoals.directory](http://api.globalgoals.directory) and
see the API response.

### Enabling HTTPS

Thanks to Dokku, setting up https is very easy. Run as `root`:

```
$ sudo dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git
```

Then set your email address:

```
$ dokku config:set --no-restart analysis DOKKU_LETSENCRYPT_EMAIL=your@email.tld
```

Then enable encryption and set up a cron job for automatic renewal:

```
$ dokku letsencrypt:enable analysis
=====> Let's Encrypt analysis... [lots of output]
$ dokku letsencrypt:cron-job --add
```

Traffic is automatically rerouted to HTTPS.
Visit [https://api.globalgoals.directory](https://api.globalgoals.directory) to
see.

## Running one-off tasks

```bash
$ ssh dokku@api.globalgoals.directory run:detached fastapi "python ./task.py"
```

You can follow the logs with:

```
$ ssh dokku@api.globalgoals.directory run:list fastapi
$ ssh root@api.globalgoals.directory docker logs -f <NAME>
```

The container will be removed automatically once the process has ended.

## Development

We use docker-compose to run the application in development.

Buildkit needs to be enabled. This is done by setting the env var
`DOCKER_BUILDKIT` to `1`. For example, by adding `export DOCKER_BUILDKIT=1`
in `~/.bashrc`.

To build and start the containers (`api` and `database`), run:

```
$ docker-compose -d up
```

The directory is automatically mounted into the container (`api`) under /app.

### Hot Reloading

Hot reloading is enabled, so any changes made to the code will instantly
reload the FastAPI server.

### Managing dependencies

[Poetry](https://github.com/python-poetry/poetry) is used to manage Python
dependencies. You need to install it locally and the run `poetry install` from
within the repo. Adding and removing dependencies via `poetry add <name>` and
`poetry remove <name>`.

When adding new dependencies, the container needs to be rebuilt with
`docker-compose build api`.

### Managing migrations

The database is started automatically via docker-compose (`database`).
Migrations are automatically run when the `api` container starts.

To autogenerate or manually manage revisions, enter the `api` container:

```
$ docker-compose exec api bash
$ alembic revision --autogenerate -m "create accounts"
```

The database has a dedicated volume mounted, so the database is persisted even
when the container is destroyed/recreated.

### Accessing the database

You can access the database by entering the database container:

```
$ docker-compose exec database psql -U postgres -d analysisdb
```

From there, you can run arbitrary SQL queries:

```
SELECT * FROM websites;
```

If a GUI is preferred for accessing the database, any kind of database
management software (e.g., [pgAdmin](https://www.pgadmin.org/) or
[TablePlus](https://tableplus.com/)) should be able to connect to
`localhost:5432` using the postgres username and password described in the
`docker-compose.yml` file.

### Backing up the database

You can back up the development database by running:

```
$ docker-compose exec -T database pg_dumpall -c -U postgres | gzip > dump_`date +%Y-%m-%d"_"%H_%M_%S`.sql.gz
```

This will create a compressed SQL dump of the database in the repository.

To restore the dump, first make sure to remove the Docker volume for the
database before importing the dump. Then run:

```
$ gzip --stdout -d dump_YYYY-mm-dd_HH_MM_SS.sql.gz | docker-compose exec -T database psql -U postgres
```

For even smaller file sizes, use the [`p7zip`](http://manpages.ubuntu.com/manpages/bionic/man1/p7zip.1.html) utility. This takes quite a while longer than `gzip` but the resulting file size is **significantly** smaller.

```
$ docker-compose exec -T database pg_dumpall -c -U postgres | p7zip > dump_`date +%Y-%m-%d"_"%H_%M_%S`.sql.7z
```

## Testing

We use pytest to test the application. Tests are defined in the `/tests`
directory.

To run the tests, start the testing container and the testing database:

```
$ docker-compose up -d api-test database-test
```

You can then follow the test output with

```
$ docker-compose logs -f api-test
```

The container is started with `pytest-watch`, which automatically reruns all
tests when a test is modified, added, or removed.

## Scraping

The web scraping is executed via
[Scrapy](https://docs.scrapy.org/en/latest/index.html), a very mature Python
framework for web scraping. The scraper will start with a single URL as an entry
point and then recursively find any internal links to other URLs on the same
domain.

Note that any links do another subdomain within the same top level domain is
**not** considered as being on the same domain. This approach was chosen
because sometimes several organizations will share the same top level domain
and it is preferable to be able to distinguish between them.

A [breadth-first approach](https://docs.scrapy.org/en/latest/faq.html?highlight=breadth%20first#does-scrapy-crawl-in-breadth-first-or-depth-first-order)
is used to ensure that higher level pages always get scraped prior to lower
level pages.

To scrape pages that rely partially or fully on JavaScript, all pages are
processed using a headless Chromium browser. This feature is handled by
[Playwright](https://github.com/scrapy-plugins/scrapy-playwright),

## References

### Language Detection

Language detection is provided via the `fasttext` library.
The pre-trained model is published under a
[CC-BY-SA 3.0 license](https://creativecommons.org/licenses/by-sa/3.0/).
Refer to
[https://fasttext.cc/docs/en/language-identification.html](https://fasttext.cc/docs/en/language-identification.html)
for more information.

**Relevant papers:**

- A. Joulin, E. Grave, P. Bojanowski, T. Mikolov, Bag of Tricks for Efficient Text Classification

- A. Joulin, E. Grave, P. Bojanowski, M. Douze, H. Jégou, T. Mikolov, FastText.zip: Compressing text classification models

### SDG Keywords

English SDG keywords are based on
[Nuria Bautista's SDG ontology](https://figshare.com/articles/dataset/SDG_ontology/11106113/1).
The ontology is published under a
[CC-BY 4.0 license](https://creativecommons.org/licenses/by/4.0/).
Refer to
[https://figshare.com/articles/dataset/SDG_ontology/11106113/1](https://figshare.com/articles/dataset/SDG_ontology/11106113/1)
for more information.

**Relevant papers:**

- Bautista-Puig, N.; Mauleón E. (2019). Unveiling the path towards sustainability: is there a research interest on sustainable goals? In the 17th International Conference on Scientometrics & Informetrics (ISSI 2019), Rome (Italy), Volume II, ISBN 978-88-3381-118-5, p.2770-2771.
