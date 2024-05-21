import json
import psycopg2

def load_data(filename='json/gdp_data.json'):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def connect_db():
    try:
        conn = psycopg2.connect(
            dbname='gdp_data',
            user='cloudwalk',
            password='EzOiDSqfrdy5cbkXhr2LQHN6eB1SzE3O',
            host='dpg-cp4lc5779t8c73ei01pg-a.oregon-postgres.render.com'
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise

def create_tables(conn):
    try:
        with conn.cursor() as cur:
            # Open and read the SQL script using Python's built-in file handling
            with open('include/init_db.sql', 'r', encoding='utf-8') as sql_file:
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
            # Batch insert into country table
            country_data = [(entry['country']['id'], entry['country']['value'], entry['countryiso3code']) for entry in data]
            cur.executemany("""
                INSERT INTO country (id, name, iso3_code)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
            """, country_data)

            # Batch insert into gdp table
            gdp_data = [(entry['country']['id'], entry['date'], entry['value']) for entry in data]
            cur.executemany("""
                INSERT INTO gdp (country_id, year, value)
                VALUES (%s, %s, %s)
                ON CONFLICT (country_id, year) DO NOTHING;
            """, gdp_data)

        conn.commit()
    except Exception as e:
        print(f"Error inserting data: {e}")
        raise
