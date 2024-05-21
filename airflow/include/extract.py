import requests
import json

def extract_data():
    base_url = "https://api.worldbank.org/v2/country/"
    countries = ["ARG", "BOL", "BRA", "CHL", "COL", "ECU", "GUY", "PRY", "PER", "SUR", "URY", "VEN"]
    indicator = "NY.GDP.MKTP.CD"
    data = []

    for country in countries:
        page = 1
        while True:
            url = f"{base_url}{country}/indicator/{indicator}?format=json&page={page}&per_page=50"
            response = requests.get(url)
            json_data = response.json()

            if not json_data:
                break

            data.extend(json_data[1])

            if len(json_data[1]) <= 50:
                break

            page += 1

    return data

