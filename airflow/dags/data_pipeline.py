from airflow import DAG
from airflow.decorators import task
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
import json
import requests
import psycopg2

# Define the default_args for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
}

# Initialize the DAG
dag = DAG(
    'gdp_data_pipeline',
    default_args=default_args,
    description='A data pipeline to extract, load, and transform GDP data',
    schedule_interval='@daily',  # You can adjust the schedule interval as needed
    catchup=False, 
)

# Task to extract data from the World Bank API
@task(task_id="extract_data", dag=dag)
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
    
    with open('/tmp/gdp_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f)

# Task to load data into PostgreSQL
@task(task_id="load_data", dag=dag)
def load_data():
    def connect_db():
        return psycopg2.connect(
            dbname='gdp_data',
            user='postgres',
            password='postgres',
            host='db'
        )

    with open('/tmp/gdp_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    conn = connect_db()
    cur = conn.cursor()

    # Create tables if they don't exist
    cur.execute(open('/app/db/init_db.sql', 'r', encoding='utf-8').read())
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

# Task to transform data and create the pivoted view
@task(task_id="transform_data", dag=dag)
def transform_data():
    conn = psycopg2.connect(
        dbname='gdp_data',
        user='postgres',
        password='postgres',
        host='db'
    )
    cur = conn.cursor()
    cur.execute(open('/app/scripts/transform.sql', 'r', encoding='utf-8').read())
    conn.commit()
    cur.close()
    conn.close()

# Define the task dependencies
extract_data_task = extract_data()
load_data_task = load_data()
transform_data_task = transform_data()

extract_data_task >> load_data_task >> transform_data_task
