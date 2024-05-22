# Use the official Python image as the base image
FROM python:3.12.1-slim as builder

# Install the PostgreSQL client tools
RUN apt-get update && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Create a tarball of the PostgreSQL client tools
RUN tar czf /postgresql-client.tar.gz /usr/lib/postgresql/

# Use the official Python image as the final image
FROM python:3.12.1-slim

# Extract the PostgreSQL client tools from the tarball
COPY --from=builder /postgresql-client.tar.gz /postgresql-client.tar.gz
RUN mkdir -p /usr/lib/postgresql/ && \
    tar xzf /postgresql-client.tar.gz -C /usr/lib/postgresql/

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Ensure the run.sh script is executable
RUN chmod +x run.sh

# Use CMD to run the run.sh script
CMD ["/app/run.sh"]