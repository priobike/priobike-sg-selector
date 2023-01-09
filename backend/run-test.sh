#!/bin/bash

# Run postgres in the background
./run-postgres.sh

# Run the migration script
poetry run python backend/manage.py migrate

# Hang around to keep the container alive, until all tests have passed
tail -f /dev/null
