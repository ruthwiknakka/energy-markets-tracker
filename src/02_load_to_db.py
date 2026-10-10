import os
import requests
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()


def fetch_prices(start="2024-01-01"):
    """Ask the EIA API for daily Brent and WTI prices."""
    url = "https://api.eia.gov/v2/petroleum/pri/spt/data/"
    params = {
        "api_key": os.getenv("EIA_API_KEY"),
        "frequency": "daily",
        "data[0]": "value",
                "facets[series][]": [
            "RBRTE",
            "RWTC",
            "EER_EPMRU_PF4_RGC_DPG",
            "EER_EPD2DXL0_PF4_RGC_DPG",
        ],
        "start": start,
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
        "length": 5000,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()   # stops with a clear error if the call failed
    return response.json()["response"]["data"]


def get_connection():
    """Phone the database using the details in .env."""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )


def upsert_prices(rows):
    """Insert rows; if (period, series) already exists, update it."""
    records = [
        (r["period"], r["series"], r["series-description"], float(r["value"]), r["units"])
        for r in rows
        if r["value"] is not None
    ]

    sql = """
        INSERT INTO spot_prices (period, series, series_description, value, units)
        VALUES %s
        ON CONFLICT (period, series) DO UPDATE SET
            series_description = EXCLUDED.series_description,
            value              = EXCLUDED.value,
            units              = EXCLUDED.units,
            loaded_at          = now()
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            execute_values(cur, sql, records)
        conn.commit()
    finally:
        conn.close()

    return len(records)


if __name__ == "__main__":
    rows = fetch_prices()
    print(f"Fetched {len(rows)} rows from the API")
    n = upsert_prices(rows)
    print(f"Upserted {n} rows into spot_prices")