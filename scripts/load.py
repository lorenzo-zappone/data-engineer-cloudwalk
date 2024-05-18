import json
import psycopg2

def load_data(filename='gdp_data.json'):
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
