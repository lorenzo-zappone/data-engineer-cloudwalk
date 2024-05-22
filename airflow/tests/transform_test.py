import unittest
from include.load import connect_db
import psycopg2

class TestTransformData(unittest.TestCase):
    def setUp(self):
        # Connect to the database
        self.conn = connect_db()

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_transform_data(self):
        # Execute the transformation task
        with self.conn.cursor() as cur:
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
            self.conn.commit()

        # Verify the existence of the pivoted_gdp view
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT 1 
                FROM information_schema.views 
                WHERE table_name = 'pivoted_gdp'
            """)
            result = cur.fetchone()
            self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()