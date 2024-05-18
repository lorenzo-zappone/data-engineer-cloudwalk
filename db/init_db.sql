CREATE TABLE IF NOT EXISTS country (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    iso3_code VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS gdp (
    country_id VARCHAR REFERENCES country(id),
    year INT,
    value NUMERIC,
    PRIMARY KEY (country_id, year)
);
