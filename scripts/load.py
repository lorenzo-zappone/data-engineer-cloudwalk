import json
import psycopg2

def load_data(filename='gdp_data.json'):
    with open(filename, 'r') as f:
        return json.load(f)

def connect_db():
    return psycopg2.connect(
        dbname='gdp_data',
        user='postgres',
        password='postgres',
        host='db'
    )

def create_tables(conn):
    with conn.cursor() as cur:
        cur.execute(open('init_db.sql', 'r').read())
    conn.commit()

def insert_data(conn, data):
    with conn.cursor() as cur:
        for entry in data[1]:
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

if __name__ == '__main__':
    data = load_data()
    conn = connect_db()
    create_tables(conn)
    insert_data(conn, data)
    conn.close()
