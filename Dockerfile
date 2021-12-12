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
    VENV_PATH="/builder/.venv"

# Set up path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Install poetry and dependencies
FROM base as builder

# Install poetry - respects $POETRY_VERSION, etc...
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -

# Copy poetry.lock and pyproject.toml
WORKDIR $BUILDER_PATH
COPY poetry.lock pyproject.toml ./

RUN --mount=type=cache,target=/builder/.venv poetry install --no-dev --remove-untracked
RUN --mount=type=cache,target=/builder/.venv cp -rT $VENV_PATH $VENV_PATH-prod

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

# Switch to non-root user (for generating migrations inside container)
RUN useradd -m -u 1000 -o -s /bin/bash user
USER user

WORKDIR /app
CMD ["/start-reload.sh"]

# `production` image used for runtime
FROM base as production
ENV FASTAPI_ENV=production
COPY --from=builder $VENV_PATH-prod $VENV_PATH
WORKDIR /app
COPY ./ /app


