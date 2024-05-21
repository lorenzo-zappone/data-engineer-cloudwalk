#!/bin/bash
set -e

# Run the extraction script
python scripts/extract.py

# Run the loading script
python scripts/load.py

# Run the SQL transformation
PGPASSWORD=postgres psql -h db -U postgres -d gdp_data -f scripts/transform.sql