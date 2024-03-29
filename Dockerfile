FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9 as base

# Adapted from https://github.com/python-poetry/poetry/discussions/1879#discussioncomment-216865
ENV \
    # Set the FastAPI entry point (api/main.py with variable api)
    MODULE_NAME=api.main \
    VARIABLE_NAME=api \
    \
    # python
    PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.1.12 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # do not ask any interactive question
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    \
    # paths
    # this is where our requirements + virtual environment will live
    BUILDER_PATH="/builder" \
    VENV_PATH="/builder/.venv" \
    PLAYWRIGHT_BROWSERS_PATH="/builder/.playwright"

# Set up path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Set up /var/lib application directory
RUN mkdir /var/lib/globalgoalsdirectory

# Install language identification model for fasttext (~ 126 MB)
# See: https://fasttext.cc/docs/en/language-identification.html
RUN curl --create-dirs -o /var/lib/globalgoalsdirectory/lid.176.bin https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin

# Add non-free packages to sources list (required for Ubuntu fonts used by
# playwright)
RUN sed -i -e's/ main/ main non-free/g' /etc/apt/sources.list
RUN apt-get update

# Install required library for python-magic
RUN apt-get install libmagic1

# Install required libraries for playwright
# Generated via: playwright install-deps --dry-run chromium
RUN apt-get install -y --no-install-recommends fonts-liberation libasound2 \
    libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 libcairo2 libcups2 \
    libdbus-1-3 libdrm2 libegl1 libgbm1 libglib2.0-0 libgtk-3-0 libnspr4 \
    libnss3 libpango-1.0-0 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 \
    libxdamage1 libxext6 libxfixes3 libxrandr2 libxshmfence1 xvfb \
    fonts-noto-color-emoji ttf-unifont libfontconfig libfreetype6 \
    xfonts-cyrillic xfonts-scalable fonts-ipafont-gothic fonts-wqy-zenhei \
    fonts-tlwg-loma-otf ttf-ubuntu-font-family

# Install poetry and dependencies
FROM base as builder

# Install poetry - respects $POETRY_VERSION, etc...
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -

# Copy poetry.lock and pyproject.toml
WORKDIR $BUILDER_PATH
COPY poetry.lock pyproject.toml ./

RUN --mount=type=cache,target=/builder/.venv poetry install --no-dev --remove-untracked
RUN --mount=type=cache,target=/builder/.venv cp -rT $VENV_PATH $VENV_PATH-prod

# Install playwright browsers
RUN --mount=type=cache,target=/builder/.venv \
    --mount=type=cache,target=/builder/.playwright \
    playwright install chromium
RUN --mount=type=cache,target=/builder/.playwright \
    cp -rT $PLAYWRIGHT_BROWSERS_PATH $PLAYWRIGHT_BROWSERS_PATH-prod

# Install dev dependencies as well
FROM builder as builder-dev
RUN --mount=type=cache,target=/builder/.venv,id=dev cp -rT $VENV_PATH-prod $VENV_PATH
RUN --mount=type=cache,target=/builder/.venv,id=dev poetry install --remove-untracked
RUN --mount=type=cache,target=/builder/.venv,id=dev cp -rT $VENV_PATH $VENV_PATH-dev

# `development` image is used during development / testing
FROM base as development
ENV FASTAPI_ENV=development

# Copy virtual environment
COPY --from=builder-dev $VENV_PATH-dev $VENV_PATH
COPY --from=builder $PLAYWRIGHT_BROWSERS_PATH-prod $PLAYWRIGHT_BROWSERS_PATH

# Switch to non-root user (for generating migrations inside container)
RUN useradd -m -u 1000 -o -s /bin/bash user
USER user

WORKDIR /app
CMD ["/start-reload.sh"]

# `production` image used for runtime
FROM base as production
ENV FASTAPI_ENV=production
COPY --from=builder $VENV_PATH-prod $VENV_PATH
COPY --from=builder $PLAYWRIGHT_BROWSERS_PATH-prod $PLAYWRIGHT_BROWSERS_PATH
WORKDIR /app
COPY ./ /app


