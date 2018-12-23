# Use an official Python runtime as a parent image
FROM python:3.7-slim-stretch

# add our user and group first to make sure their IDs get assigned consistently
RUN groupadd -r tabletop && useradd -r -m -g tabletop tabletop

ENV PYTHONUNBUFFERED 1

ENV PIP_NO_CACHE_DIR off
ENV PIP_DISABLE_PIP_VERSION_CHECK on

RUN mkdir -p /usr/src/tabletop
WORKDIR /usr/src/tabletop

RUN set -ex \
    && apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        gcc \
        git \
        gosu \
        libffi-dev \
        libpq-dev \
        libxml2-dev \
        libxslt-dev \
        openssl \
        ssh \
        wget \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python

COPY pyproject.toml /usr/src/tabletop/
RUN poetry install --no-dev

COPY . /usr/src/tabletop

ENV PATH /usr/src/tabletop/bin:$PATH

# Make port 8080 available to the world outside this container
EXPOSE 8000

ENTRYPOINT ["docker-entrypoint"]

# Run Zeus
CMD ["gunicorn", "tabletop.wsgi" "--log-file -"]
