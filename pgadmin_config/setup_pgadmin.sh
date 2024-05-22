#!/bin/bash

# Set up the pgAdmin tool

# Create a new server group
echo "CREATE SERVER GROUP gdp_data_group;" | psql -h db_app -U postgres gdp_data

# Create a new server
echo "CREATE SERVER gdp_data_server WITH DB_NAME='gdp_data', HOST='db', PORT='5432', USER='postgres', PASSWORD='postgres';" | psql -h db_app -U postgres gdp_data

# Add the server to the server group
echo "ADD SERVER gdp_data_server TO SERVER GROUP gdp_data_group;" | psql -h db_app -U postgres gdp_data