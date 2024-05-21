#!/bin/bash

# Start PgAdmin in the background
/entrypoint.sh &

# Wait for PgAdmin to start
sleep 10

# Define connection settings
SERVER_NAME="PostgreSQL Database"
SERVER_HOSTNAME="db"
SERVER_PORT=5432
SERVER_USERNAME="postgres"
SERVER_PASSWORD="postgres"
SERVER_DBNAME="gdp_data"

# Add a new server in PgAdmin
curl -s --header "Content-Type: application/json" \
  --request POST \
  --data "{\"name\":\"${SERVER_NAME}\",\"host\":\"${SERVER_HOSTNAME}\",\"port\":${SERVER_PORT},\"username\":\"${SERVER_USERNAME}\",\"password\":\"${SERVER_PASSWORD}\",\"maintenance_db\":\"${SERVER_DBNAME}\"}" \
  http://localhost:8085/setup-server

# Keep the container running
tail -f /dev/null
