from airflow import DAG
from airflow.decorators import task, dag
from airflow.operators.python import BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
import json
import requests
import psycopg2
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
}

@dag(
    dag_id='gdp_data_pipeline',
    default_args=default_args,
    description='A data pipeline to extract, load, and transform GDP data',
    schedule_interval='@yearly',  # Adjust the schedule interval as needed
    catchup=False,
    tags=['cloudwalk'],
)

#TODO
# add feature to check if the data is already loaded before continuing

def gdp_data_pipeline():
    @task
    def extract_data():
        url = "https://api.worldbank.org/v2/country/ARG;BOL;BRA;CHL;COL;ECU;GUY;PRY;PER;SUR;URY;VEN/indicator/NY.GDP.MKTP.CD?format=json&per_page=50&page={}"
        page = 1
        all_data = []
        while True:
            response = requests.get(url.format(page))
            data = response.json()
            if not data[1]:  # If there is no more data
                break
            all_data.extend(data[1])
            page += 1

        with open('include/gdp_data.json', 'w', encoding='utf-8') as f:
            json.dump(all_data, f)

    @task
    def load_data():
        def connect_db():
            return psycopg2.connect(
                dbname='gdp_data',
                user='cloudwalk',
                password='EzOiDSqfrdy5cbkXhr2LQHN6eB1SzE3O',
                host='dpg-cp4lc5779t8c73ei01pg-a.oregon-postgres.render.com'
            )

        with open('include/gdp_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        conn = connect_db()
        cur = conn.cursor()

        # Create tables if they don't exist
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS country (
                    id VARCHAR PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    iso3_code VARCHAR NOT NULL,
                );

                CREATE TABLE IF NOT EXISTS gdp (
                    country_id VARCHAR REFERENCES country(id),
                    year INT,
                    value NUMERIC,
                    PRIMARY KEY (country_id, year));
        """)
        conn.commit()

        # Insert data
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
        cur.close()
        conn.close()

    @task
    def transform_data():
        conn = psycopg2.connect(
            dbname='gdp_data',
            user='cloudwalk',
            password='EzOiDSqfrdy5cbkXhr2LQHN6eB1SzE3O',
            host='dpg-cp4lc5779t8c73ei01pg-a.oregon-postgres.render.com'
        )
        cur = conn.cursor()
        cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM information_schema.views 
                        WHERE table_name = 'pivoted_gdp'
                    ) THEN
                        EXECUTE '
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
';
                    END IF;
                END $$;
        """)
        conn.commit()
        cur.close()
        conn.close()

    extract_data() >> load_data() >> transform_data()

dag = gdp_data_pipeline()
