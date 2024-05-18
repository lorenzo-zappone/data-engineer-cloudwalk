# GDP Data Ingestion and Transformation Pipeline

## Introduction

This project demonstrates a data ingestion and transformation pipeline that extracts GDP data for South American countries from the World Bank API, loads the data into a PostgreSQL database, and transforms it to produce a pivoted report of the last 5 years' GDP values for each country, presented in billions.

## Project Structure


├── db

│ └── init_db.sql # SQL script to initialize the database schema

├── scripts

│ ├── extract.py # Script to extract data from the World Bank API

│ ├── load.py # Script to load data into the PostgreSQL database

│ └── transform.sql # SQL script to create the pivoted view

├── Dockerfile # Dockerfile for the application

├── docker-compose.yml # Docker Compose file to orchestrate services

├── requirements.txt # Python dependencies

├── run.sh # Shell script to run the entire ETL process

└── README.md # Project documentation

## Setup and Execution

### Prerequisites

- Docker
- Docker Compose

### Steps to Execute

1. **Clone the repository:**

    ```bash
    git clone https://github.com/lorenzo-zappone/data-engineer-cloudwalk.git
    cd data-engineer-cloudwalk
    ```

2. **Build and run the Docker containers:**

    ```bash
    docker-compose up --build -d
    ```

    This command will:
    - Build the Docker images.
    - Start the PostgreSQL database container.
    - Start the pgAdmin container.
    - Run the ETL process in the application container.

3. **Access pgAdmin:**

    After running the containers, pgAdmin will be available at `http://localhost:5050`.

    - **Email:** `admin@admin.com`
    - **Password:** `admin`

    You can use pgAdmin to verify the data in the PostgreSQL database.

## Design Decisions and Assumptions

### Assumptions

- The World Bank API endpoint can have multiple pages. The `extract.py` script handles pagination to ensure all data is retrieved.
- The data is stored in two tables: `country` and `gdp`. The `country` table stores country metadata, while the `gdp` table stores GDP values for each year.
- The ETL process assumes that the database and tables are initially empty. The `ON CONFLICT` clause in the `INSERT` statements ensures that duplicate entries are not created.

### Design Decisions

1. **Dockerization:**
   - The project uses Docker to ensure consistent environments and dependencies across different systems.
   - Docker Compose is used to orchestrate multiple services (PostgreSQL and pgAdmin).

2. **Data Extraction:**
   - The `extract.py` script fetches GDP data from the World Bank API and saves it to a local JSON file.

3. **Data Loading:**
   - The `load.py` script reads the JSON data and inserts it into the PostgreSQL database. It handles potential conflicts by using `ON CONFLICT` clauses.

4. **Data Transformation:**
   - The `transform.sql` script creates a pivoted view `pivoted_gdp` to facilitate reporting. This view presents the last 5 years' GDP values in billions.

5. **Automation:**
   - The `run.sh` script automates the ETL process, including data extraction, loading, and transformation.

## Running the ETL Process Manually

If you need to run the ETL process manually, you can do so by executing the scripts in the following order:

1. **Extract Data:**

    ```bash
    docker-compose exec app python scripts/extract.py
    ```

2. **Load Data:**

    ```bash
    docker-compose exec app python scripts/load.py
    ```

3. **Transform Data:**

    ```bash
    docker-compose exec db psql -U postgres -d gdp_data -f /files/transform.sql
    ```

## Conclusion

This project provides a robust and scalable solution for ingesting and transforming GDP data. The use of Docker ensures that the solution can be easily deployed and maintained. The documentation and clear structure make it easy to understand and extend.

If you have any questions or need further assistance, please feel free to contact zappone500@gmail.com.
