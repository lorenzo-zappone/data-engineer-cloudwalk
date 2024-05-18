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

# Ensure the run.sh and setup_pgadmin.sh script is executable
RUN chmod +x pgadmin/setup_pgadmin.sh
RUN chmod +x /app/run.sh


# Use CMD to run the run.sh script
CMD ["./run.sh"]
