FROM postgis/postgis:14-3.3 AS builder
# This docker image is based on the bullseye operating system
# See: https://github.com/postgis/docker-postgis/blob/master/14-3.3/Dockerfile

# Install libraries needed for GeoDjango and PostGIS
# See https://docs.djangoproject.com/en/3.2/ref/contrib/gis/install/geolibs/
RUN apt-get update && apt-get install -y \
  binutils \
  libproj-dev \
  gdal-bin

# Install Postgres client to check liveness of the database
RUN apt-get install -y postgresql-client

# Install osm2pgsql to load the osm-data into the database
RUN apt-get install -y osm2pgsql

# Install Python and a dependency for psycopg2
RUN apt-get install -y python3 python3-pip libpq-dev

# Install Poetry as the package manager for this application
RUN pip install poetry

WORKDIR /code

# Install Python dependencies separated from the
# run script to enable Docker caching
ADD pyproject.toml /code
# Install all dependencies
RUN poetry install

# Install CURL for healthcheck
RUN apt-get install -y curl

# Expose Django port, DO NOT EXPOSE THE DATABASE PORT!
EXPOSE 8000

COPY . /code

# Define the FROST API from which we will fetch the things
ARG FROST_API=https://priobike.vkw.tu-dresden.de/production/priobike-frost-mirror/FROST-Server/v1.1
ARG FROST_FILTER=%28Datastreams%2Fproperties%2FserviceName%20eq%20%27HH_STA_traffic_lights%27%29

ENV FROST_API=$FROST_API
ENV FROST_FILTER=$FROST_FILTER

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV POSTGRES_NAME=sgselector-db
ENV POSTGRES_USER=sgselector-user
ENV POSTGRES_PASSWORD=sgselector-password
ENV POSTGRES_DB=sgselector-db
ENV POSTGRES_HOST=localhost
ENV POSTGRES_PORT=5432

ENV HEALTHCHECK_TOKEN=healthcheck-token

# Use this argument to invalidate the cache of subsequent steps.
ARG CACHE_DATE=1970-01-01

FROM builder AS test
# Only run postgres to execute tests
CMD "./run-test.sh"

FROM builder AS dev
ENV DJANGO_DEBUG_MODE=True
# Run the development server
RUN ./run-preheating-dev.sh
HEALTHCHECK --interval=60s --timeout=10s --retries=5 --start-period=10s \
  CMD curl --fail http://localhost:8000/healthcheck?token=healthcheck-token || exit 1
CMD "./run-dev.sh"

FROM builder AS production
ENV DJANGO_DEBUG_MODE=False
# Preheat our database, by running migrations and pre-loading data
RUN ./run-preheating-prod.sh
HEALTHCHECK --interval=60s --timeout=10s --retries=5 --start-period=10s \
  CMD curl --fail http://localhost:8000/healthcheck?token=healthcheck-token || exit 1
CMD "./run-prod.sh"

FROM bikenow.vkw.tu-dresden.de/priobike/priobike-nginx:release AS static_proxy
# Copy the static files from the production container
COPY --from=production /code/backend/static /usr/share/nginx/html