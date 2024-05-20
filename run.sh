#!/bin/bash
set -e

# Run the extraction script
python scripts/extract.py

# Run the loading script
python scripts/load.py

# Run the SQL transformation
# psql -h db -U postgres -d gdp_data -f scripts/transform.sql

PGPASSWORD=EzOiDSqfrdy5cbkXhr2LQHN6eB1SzE3O psql -h dpg-cp4lc5779t8c73ei01pg-a.oregon-postgres.render.com -U cloudwalk -d gdp_data -f scripts/transform.sql