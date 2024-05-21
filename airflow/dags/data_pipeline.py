from airflow import DAG
from airflow.decorators import task, dag
from airflow.operators.python import BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
from include.extract import extract_data
from include.load import load_data, connect_db, create_tables, insert_data
import json
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

def gdp_data_pipeline():
    @task
    def extract_data_task():
        data = extract_data()
        with open("json/gdp_data.json", "w") as f:
            json.dump(data, f)

    @task
    def load_data_task():
        with open("json/gdp_data.json", "r") as f:
            data = json.load(f)
        conn = connect_db()
        create_tables(conn)
        insert_data(conn, data)
        conn.close()

    @task
    def transform_data_task():
        conn = connect_db()
        try:
            with conn.cursor() as cur:
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
        except Exception as e:
            print(f"Error transforming data: {e}")
            raise
        finally:
            conn.close()


    extract_data_task() >> load_data_task() >> transform_data_task()

dag = gdp_data_pipeline()
