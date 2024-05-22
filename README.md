# GDP Data Pipeline

## Introduction

This project demonstrates a data ingestion and transformation pipeline that extracts GDP data for South American countries from the World Bank API, loads the data into a PostgreSQL database, and transforms it to produce a pivoted report of the last 5 years' GDP values for each country, presented in billions.

## Project Structure

``` php	
    ├── db
        └── init_db.sql # SQL script to initialize the database schema
    ├── scripts
        ├── extract.py # Script to extract data from the World Bank API
        ├── load.py # Script to load data into the PostgreSQL database
        └── transform.sql # SQL script to create the pivoted view
    ├── Dockerfile # Dockerfile for the application
    ├── docker-compose.yml # Docker Compose file to orchestrate services
    ├── requirements.txt # Python dependencies
    ├── run.sh # Shell script to run the entire ETL process
    └── README.md # Project documentation
```	

## Setup and Execution

### Prerequisites

- Docker
- Docker Compose
- Poetry (for dependency management and packaging)
- **Astro CLI** to run Apache Airflow **

### Installing Prerequisites

**Docker and Docker Compose:**
Follow the installation instructions for your OS on the [Docker website](https://docs.docker.com/get-docker/).

**Poetry:**
Follow the installation instructions on the [Poetry website](https://python-poetry.org/docs/#installation).

****Optional step - Astro CLI:**
Follow the installation instructions for your OS:

- **Windows:**
    ```bash
    winget install -e --id Astronomer.Astro
    ```

- **MacOS:**
    ```bash
    brew install astro
    ```

- **Linux:**
    ```bash
    curl -sSL install.astronomer.io | sudo bash -s
    ```

## Steps to Execute

1. **Clone the repository:**

    ```bash
    git clone https://github.com/lorenzo-zappone/data-engineer-cloudwalk.git
    cd data-engineer-cloudwalk
    ```

2. **Install dependencies using Poetry:**

    ```bash
    poetry install
    ```

3. **Build and run the Docker containers:**

    ```bash
    docker-compose up --build -d
    ```

    This command will:
    - Build the Docker images.
    - Start the PostgreSQL database container.
    - Start the pgAdmin container.
    - Run the ETL process in the application container.

4. **Access pgAdmin:**

    After running the containers, pgAdmin will be available at `http://localhost:5050`.

    - **Email:** `admin@admin.com`
    - **Password:** `admin`
    
    - Add Server information

    ![alt text](https://github.com/lorenzo-zappone/data-engineer-cloudwalk/blob/main/pics/step-01.png)

    ![alt text](https://github.com/lorenzo-zappone/data-engineer-cloudwalk/blob/main/pics/step-02.png)

    ![alt text](https://github.com/lorenzo-zappone/data-engineer-cloudwalk/blob/main/pics/step-03.png)


5. **Validate the tables in the database:**

    - Log in to pgAdmin.
    - Connect to the PostgreSQL server using the credentials provided in the `docker-compose.yaml` file.
    - Verify that the `country` and `gdp` tables are created and populated.

## Optional configuration
6. **Navigate to the Airflow folder:**

    ```bash
    cd airflow
    ```

7. **Start Airflow using Astro CLI:**

    ```bash
    astro dev start --wait 3m
    ```

    - Open your browser and go to `http://localhost:8080` to access the Airflow web UI.

    - **User:** `admin`
    - **Password:** `admin`

    ### Repeat step 4 to connect to the `cloud-DB` used with Apache Airflow.

    - **Database:** `gdp_data`
    - **User:** `cloudwalk`
    - **Password:** `EzOiDSqfrdy5cbkXhr2LQHN6eB1SzE3O` 
    - **Host** `dpg-cp4lc5779t8c73ei01pg-a.oregon-postgres.render.com`   

## Design Decisions and Assumptions

### Assumptions

- The World Bank API endpoint can have multiple pages. The `extract.py` script handles pagination to ensure all data is retrieved.
- The data is stored in two tables: `country` and `gdp`. The `country` table stores country metadata, while the `gdp` table stores GDP values for each year.
- The ETL process assumes that the database and tables are initially empty. The `ON CONFLICT` clause in the `INSERT` statements ensures that duplicate entries are not created.

- The `pivoted_gdp` view presents the last 5 years' GDP values for each country in billions.

  **Assumption**: For the missing GDP values for Venezuela ("VE"), the data in the World Bank shows the `the most recent gdp is from 2014` and for the missing data in 2023, there isn't any indeed.

  | id  | name            | iso3_code | 2019  | 2020  | 2021  | 2022  | 2023  |
  | --- | --------------- | --------- | ----- | ----- | ----- | ----- | ----- |
  | AR  | Argentina       | ARG       | 447.75| 385.74| 487.90| 631.13| -     |
  | BO  | Bolivia         | BOL       | 40.90 | 36.63 | 40.41 | 44.01 | -     |
  | BR  | Brazil          | BRA       | 1873.29| 1476.11| 1649.62| 1920.10| -    |
  | CL  | Chile           | CHL       | 278.60| 254.26| 316.58| 301.02| -     |
  | CO  | Colombia        | COL       | 323.03| 270.15| 318.51| 343.62| -     |
  | EC  | Ecuador         | ECU       | 108.11| 99.29 | 106.17| 115.05| -     |
  | GY  | Guyana          | GUY       | 5.17  | 5.47  | 8.04  | 14.72 | -     |
  | PY  | Paraguay        | PRY       | 37.93 | 35.43 | 39.95 | 41.72 | -     |
  | PE  | Peru            | PER       | 228.33| 201.95| 223.72| 242.63| -     |
  | SR  | Suriname        | SUR       | 4.02  | 2.91  | 3.08  | 3.62  | -     |
  | UY  | Uruguay         | URY       | 62.05 | 53.67 | 61.41 | 71.18 | -     |
  | VE  | Venezuela, RB   | VEN       | -     | -     | -     | -     | -     |


### Design Decisions

1. **Dockerization:**
   - The project uses Docker to ensure consistent environments and dependencies across different systems.
   - Docker Compose is used to orchestrate multiple services (PostgreSQL and pgAdmin).

2. **Data Extraction:**
   - The `extract.py` script fetches GDP data from the World Bank API and saves it to a local JSON file.
   
```python
    import requests
    import json

    def extract_data():
        base_url = "https://api.worldbank.org/v2/country/"
        countries = ["ARG", "BOL", "BRA", "CHL", "COL", "ECU", "GUY", "PRY", "PER", "SUR", "URY", "VEN"]
        indicator = "NY.GDP.MKTP.CD"
        data = []

        for country in countries:
            page = 1
            while True:
                url = f"{base_url}{country}/indicator/{indicator}?format=json&page={page}&per_page=50"
                response = requests.get(url)
                json_data = response.json()

                if not json_data:
                    break

                data.extend(json_data[1])

                if len(json_data[1]) <= 50:
                    break

                page += 1

        return data

    if __name__ == "__main__":
        data = extract_data()
        with open("json/gdp_data.json", "w") as f:
            json.dump(data, f)

```

3. **Data Loading:**
   - The `load.py` script reads the JSON data and inserts it into the PostgreSQL database. It handles potential conflicts by using `ON CONFLICT` clauses.

```python
import json
import psycopg2

def load_data(filename='json/gdp_data.json'):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def connect_db():
    try:
        conn = psycopg2.connect(
            dbname='gdp_data',
            user='postgres',
            password='postgres',
            host='db'
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise

def create_tables(conn):
    try:
        with conn.cursor() as cur:
            # Open and read the SQL script using Python's built-in file handling
            with open('db/init_db.sql', 'r', encoding='utf-8') as sql_file:
                sql_script = sql_file.read()

            # Execute the SQL script
            cur.execute(sql_script)
            
        conn.commit()
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise

def insert_data(conn, data):
    try:
        with conn.cursor() as cur:
            for entry in data:
                country_id = entry['country']['id']
                country_name = entry['country']['value']
                iso3_code = entry['countryiso3code']
                year = entry['date']
                value = entry['value']

                cur.execute("""
                    INSERT INTO country (id, name, iso3_code)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                """, (country_id, country_name, iso3_code))

                cur.execute("""
                    INSERT INTO gdp (country_id, year, value)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (country_id, year) DO NOTHING;
                """, (country_id, year, value))
                    
        conn.commit()
    except Exception as e:
        print(f"Error inserting data: {e}")
        raise

if __name__ == '__main__':
    data = load_data()
    conn = connect_db()
    create_tables(conn)
    insert_data(conn, data)
    conn.close()
```

4. **Data Transformation:**
   - The `transform.py` script creates a pivoted view `pivoted_gdp` to facilitate reporting. This view presents the last 5 years' GDP values in billions.

```python
import psycopg2

def connect_db():
    try:
        conn = psycopg2.connect(
            dbname='gdp_data',
            user='postgres',
            password='postgres',
            host='db'
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise

def create_view(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE VIEW pivoted_gdp AS
                SELECT
                    country.id,
                    country.name,
                    country.iso3_code,
                    ROUND(MAX(CASE WHEN gdp.year = 2019 THEN gdp.value / 1e9 END), 2) AS "2019",
                    ROUND(MAX(CASE WHEN gdp.year = 2020 THEN gdp.value / 1e9 END), 2) AS "2020",
                    ROUND(MAX(CASE WHEN gdp.year = 2021 THEN gdp.value / 1e9 END), 2) AS "2021",
                    ROUND(MAX(CASE WHEN gdp.year = 2022 THEN gdp.value / 1e9 END), 2) AS "2022",
                    ROUND(MAX(CASE WHEN gdp.year = 2023 THEN gdp.value / 1e9 END), 2) AS "2023"
                FROM
                    country
                JOIN
                    gdp ON country.id = gdp.country_id
                GROUP BY
                    1, 2, 3
                ORDER BY
                    2 ASC;
            """)
            
        conn.commit()
    except Exception as e:
        print(f"Error creating view: {e}")
        raise

if __name__ == '__main__':
    conn = connect_db()
    create_view(conn)
    conn.close()
```

5. **Automation:**
   - The `run.sh` script automates the ETL process, including data extraction, loading, and transformation when the docker container is created.

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
    docker-compose exec app python scripts/transform.py
    ```

## Conclusion

This project effectively demonstrates the end-to-end process of extracting, transforming, and loading GDP data for South American countries from the World Bank API into a PostgreSQL database. The use of Docker and Docker Compose ensures that the environment is consistent and easily replicable, making the setup straightforward and efficient. The inclusion of Poetry for dependency management further simplifies the process, ensuring that all necessary packages are installed seamlessly.

The project is well-structured, with clear scripts for each stage of the ETL process:

1. **Data Extraction:** The `extract.py` script handles the retrieval of data from the World Bank API, including pagination to ensure comprehensive data collection.
2. **Data Loading:** The `load.py` script inserts the extracted data into the PostgreSQL database, with safeguards to prevent duplicate entries.
3. **Data Transformation:** The SQL script `transform.py` creates a pivoted view to present the last five years of GDP data in a user-friendly format, facilitating easy analysis and reporting.

Additionally, the project includes optional steps to integrate Apache Airflow for orchestrating the ETL workflow, demonstrating a forward-thinking approach to automation and scalability.

By following the detailed setup and execution instructions, users can quickly deploy the solution and start analyzing the GDP data. The automation script `run.sh` further enhances usability by streamlining the ETL process. Also, the addition of Airflow can be used to integrate seemlessly with a cloud-based approach.

In summary, this project provides a comprehensive, scalable, and easy-to-deploy solution for GDP data ingestion and transformation, making it a valuable tool for data engineers and analysts. If further assistance is needed, please contact zappone500@gmail.com.
