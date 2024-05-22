#!/bin/bash
set -e

# Run the extraction script
python scripts/extract.py

# Run the loading script
python scripts/load.py

# Run the SQL transformation
python scripts/transform.py