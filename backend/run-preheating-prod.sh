#!/bin/bash

# Normally, the docker container will need to process data when it is started.
# This will cause a lot of time and redundant comutational effort to be wasted.
# So, we can preheat the docker images to avoid this problem. This script is 
# part of the Dockerfile, and will be executed when the docker image is built.

echo "Preheating the docker image..."

# Run postgres in the background
./run-postgres.sh

# Run the migration script
poetry run python backend/manage.py migrate

# Load the crossings
poetry run python backend/manage.py load_crossings data/HH_WFS_Lichtsignalanlagen

# Load the lsas from the remote
poetry run python backend/manage.py load_lsas --api ${FROST_API} --filter ${FROST_FILTER}

# Sync the crossings to the loaded lsas
poetry run python backend/manage.py sync_crossings

echo "Preheating complete!"
