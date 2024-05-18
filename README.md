# Data Engineer Test Solution

## Introduction
This repository contains the solution for the data ingestion pipeline challenge. The pipeline extracts GDP data for South American countries from the World Bank API, loads it into a SQL database, and generates a pivoted report for the last 5 years.

## Solution Overview
The solution comprises the following components:
- **Data Extraction:** A Python script to fetch GDP data from the World Bank API.
- **Data Loading:** The extracted data is loaded into a PostgreSQL database.
- **Data Transformation:** A SQL query to pivot the data and generate the required report.
- **Docker Environment:** Docker Compose is used to orchestrate the services.

## Repository Structure
