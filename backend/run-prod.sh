#!/bin/bash

# Run postgres in the background
./run-postgres.sh

# Run gunicorn
cd backend
poetry run gunicorn backend.wsgi:application --workers 4 --bind 0.0.0.0:8000