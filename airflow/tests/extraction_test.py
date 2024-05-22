import unittest
from include.extract import extract_data
import json

class TestExtractData(unittest.TestCase):
    def test_extract_data(self):
        data = extract_data()
        self.assertIsNotNone(data)
        self.assertTrue(len(data) > 0)

        # Save the extracted data to a JSON file for further testing
        with open("test_json/gdp_data.json", "w") as f:
            json.dump(data, f)

if __name__ == '__main__':
    unittest.main()