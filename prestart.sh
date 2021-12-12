#! /usr/bin/env bash

# This file is executed by the uvicorn-gunicorn-docker image before our
# application starts.
# See: https://github.com/tiangolo/uvicorn-gunicorn-docker/blob/master/docker-images/app/prestart.sh

# Run migrations
alembic upgrade head