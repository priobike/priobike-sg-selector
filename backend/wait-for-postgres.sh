#!/bin/bash
#!/usr/bin/env bash

echo "Waiting for postgres server..."
# Await PostGreSQL server to become available
RETRIES=20
while [ "$RETRIES" -gt 0 ]
do
  PG_STATUS="$(pg_isready -d ${POSTGRES_NAME} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -U ${POSTGRES_USER})"
  PG_EXIT=$(echo $?)
  if [ "$PG_EXIT" = "0" ];
    then
      RETRIES=0
  fi
  sleep 0.5
done
echo "Postgres server is up!"
