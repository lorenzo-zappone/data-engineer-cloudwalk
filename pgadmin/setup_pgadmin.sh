#!/bin/bash

# Wait for pgAdmin to start
sleep 20

# Define connection settings
SERVER_NAME="CloudWalk"
SERVER_HOSTNAME="dpg-cp4lc5779t8c73ei01pg-a.oregon-postgres.render.com"
SERVER_PORT=5432
SERVER_USERNAME="cloudwalk"
SERVER_PASSWORD="EzOiDSqfrdy5cbkXhr2LQHN6eB1SzE3O"
SERVER_DBNAME="gdp_data"

# Define pgadmin
PGADMIN_DEFAULT_EMAIL="admin@admin.com"
PGADMIN_DEFAULT_PASSWORD="admin"

# Ensure PGADMIN_DEFAULT_EMAIL and PGADMIN_DEFAULT_PASSWORD are set
if [ -z "$PGADMIN_DEFAULT_EMAIL" ] || [ -z "$PGADMIN_DEFAULT_PASSWORD" ]; then
  echo "PGADMIN_DEFAULT_EMAIL and PGADMIN_DEFAULT_PASSWORD must be set."
  exit 1
fi

# Fetch the CSRF token and cookies
curl 'http://localhost:80/login' \
  --silent \
  --cookie-jar cookies.txt \
  --output /dev/null

CSRF_TOKEN=$(grep -oP '(?<=pgAdmin4 CSRF Token: ).*' cookies.txt)

# Log in to pgAdmin to establish session
curl 'http://localhost:5050/login' \
  --silent \
  --cookie cookies.txt \
  --data "email=${PGADMIN_DEFAULT_EMAIL}&password=${PGADMIN_DEFAULT_PASSWORD}" \
  --header "X-CSRFToken: $CSRF_TOKEN" \
  --output /dev/null

# Fetch a new CSRF token after login
CSRF_TOKEN=$(curl 'http://localhost:5050/browser/' \
  --silent \
  --cookie cookies.txt \
  | grep -oP '(?<=pgAdmin4 CSRF Token: ).*')

# Add a new server in pgAdmin
curl -s --header "Content-Type: application/json" \
  --header "X-CSRFToken: $CSRF_TOKEN" \
  --cookie cookies.txt \
  --request POST \
  --data "{
    \"name\":\"${SERVER_NAME}\",
    \"group\":\"Servers\",
    \"host\":\"${SERVER_HOSTNAME}\",
    \"port\":${SERVER_PORT},
    \"username\":\"${SERVER_USERNAME}\",
    \"password\":\"${SERVER_PASSWORD}\",
    \"sslmode\":\"prefer\",
    \"maintenance_db\":\"${SERVER_DBNAME}\"
  }" \
  http://localhost:5050/browser/server/

# Keep the container running
tail -f /dev/null
