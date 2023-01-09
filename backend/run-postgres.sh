#!/bin/bash

# Run postgres in the background
echo "Starting postgres..."
/usr/local/bin/docker-entrypoint.sh postgres \
  -c log_destination=stderr \
  -c max_parallel_workers_per_gather=4 \
  &
pid=$!
echo "Postgres started with pid $pid"

./wait-for-postgres.sh
