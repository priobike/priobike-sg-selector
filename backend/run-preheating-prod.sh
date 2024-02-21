#!/bin/bash

# Normally, the docker container will need to process data when it is started.
# This will cause a lot of time and redundant comutational effort to be wasted.
# So, we can preheat the docker images to avoid this problem. This script is 
# part of the Dockerfile, and will be executed when the docker image is built.

echo "Preheating the docker image..."

# Run postgres in the background
./run-postgres.sh

# Check if previous command failed. If it did, exit
ret=$?
if [ $ret -ne 0 ]; then
    echo "Failed to start postgres"
    exit $ret
fi

# Run the migration script
poetry run python backend/manage.py migrate

# Check if previous command failed. If it did, exit
ret=$?
if [ $ret -ne 0 ]; then
    echo "Migration failed"
    exit $ret
fi

# Load the crossings
poetry run python backend/manage.py load_crossings data/HH_WFS_Lichtsignalanlagen

# Check if previous command failed. If it did, exit
ret=$?
if [ $ret -ne 0 ]; then
    echo "Failed to load crossings data."
    exit $ret
fi

# Load the lsas from the remote
poetry run python backend/manage.py load_lsas --api ${FROST_API} --filter ${FROST_FILTER}

# Check if previous command failed. If it did, exit
ret=$?
if [ $ret -ne 0 ]; then
    echo "Failed to load SGs from API."
    exit $ret
fi


# Sync the crossings to the loaded lsas
poetry run python backend/manage.py sync_crossings

# Check if previous command failed. If it did, exit
ret=$?
if [ $ret -ne 0 ]; then
    echo "Failed to sync crossings."
    exit $ret
fi

# Save all SGs to a gzipped json file in the static directory
poetry run python backend/manage.py dump_sgs

# Check if previous command failed. If it did, exit
ret=$?
if [ $ret -ne 0 ]; then
    echo "Failed to dump SGs."
    exit $ret
fi

echo "Preheating complete!"
