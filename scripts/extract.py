import requests
import json

# World Bank API endpoint
url = "https://api.worldbank.org/v2/country/ARG;BOL;BRA;CHL;COL;ECU;GUY;PRY;PER;SUR;URY;VEN/indicator/NY.GDP.MKTP.CD?format=json&page=1&per_page=50"

def fetch_gdp_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def save_data(data, filename='gdp_data.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == '__main__':
    data = fetch_gdp_data(url)
    save_data(data)
