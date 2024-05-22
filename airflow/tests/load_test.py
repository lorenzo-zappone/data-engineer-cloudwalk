import unittest
from include.load import load_data, connect_db, create_tables, insert_data
import psycopg2
import json

class TestLoadData(unittest.TestCase):
    def setUp(self):
        # Connect to the database
        self.conn = connect_db()
        # Create the tables
        create_tables(self.conn)

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_load_data(self):
        # Load the test data from the JSON file
        with open("test_json/gdp_data.json", "r") as f:
            data = json.load(f)

        # Insert the data into the database
        insert_data(self.conn, data)

        # Verify the data in the database
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM country")
            countries = cur.fetchall()
            self.assertTrue(len(countries) > 0)

            cur.execute("SELECT * FROM gdp")
            gdp_values = cur.fetchall()
            self.assertTrue(len(gdp_values) > 0)

if __name__ == '__main__':
    unittest.main()