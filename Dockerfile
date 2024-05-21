# Use the official Python image.
FROM python:3.12.1-slim

# Install the PostgreSQL client tools
RUN apt-get update && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Ensure the run.sh and setup_pgadmin.sh scripts are executable
RUN chmod +x pgadmin_config/setup_pgadmin.sh \
    && chmod +x run.sh 

# Use CMD to run both setup_pgadmin.sh and run.sh
CMD ["/bin/bash", "-c", "/docker-entrypoint-initdb.d/setup_pgadmin.sh && /app/run.sh"]
