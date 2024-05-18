CREATE VIEW pivoted_gdp AS
SELECT
    country.id,
    country.name,
    country.iso3_code,
    MAX(CASE WHEN gdp.year = 2019 THEN gdp.value / 1e9 END) AS "2019",
    MAX(CASE WHEN gdp.year = 2020 THEN gdp.value / 1e9 END) AS "2020",
    MAX(CASE WHEN gdp.year = 2021 THEN gdp.value / 1e9 END) AS "2021",
    MAX(CASE WHEN gdp.year = 2022 THEN gdp.value / 1e9 END) AS "2022",
    MAX(CASE WHEN gdp.year = 2023 THEN gdp.value / 1e9 END) AS "2023"
FROM
    country
JOIN
    gdp ON country.id = gdp.country_id
GROUP BY
    country.id, country.name, country.iso3_code;
