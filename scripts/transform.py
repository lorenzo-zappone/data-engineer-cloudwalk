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