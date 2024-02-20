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

# Load the lsas from the .json dump
poetry run python backend/manage.py load_lsas_from_file --path data/sgs-2023-01-11T14_30_50.004510.json

# Sync the crossings to the loaded lsas
poetry run python backend/manage.py sync_crossings

# Save all SGs to a gzipped json file in the static directory
poetry run python backend/manage.py dump_sgs

echo "Preheating complete!"
