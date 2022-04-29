FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install libraries needed for GeoDjango and PostGIS
# See https://docs.djangoproject.com/en/3.2/ref/contrib/gis/install/geolibs/
RUN apt-get update && apt-get install -y \
  binutils \
  libproj-dev \
  gdal-bin

# Install Postgres client to check liveness of the database
RUN apt-get install -y postgresql-client

# Install Poetry as the package manager for this application
RUN pip install poetry

WORKDIR /code

# Install Python dependencies separated from the
# run script to enable Docker caching
ADD pyproject.toml /code
RUN poetry install --no-interaction --no-ansi --no-dev

ADD . /code