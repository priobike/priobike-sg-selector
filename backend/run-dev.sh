#!/bin/bash

# Run postgres in the background
./run-postgres.sh

# Run the development server
cd backend
poetry run python manage.py migrate
poetry run python manage.py runserver 0.0.0.0:8000