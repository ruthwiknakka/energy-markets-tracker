import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

url = "https://api.eia.gov/v2/petroleum/pri/spt/data/"
params = {
    "api_key": os.getenv("EIA_API_KEY"),
    "frequency": "daily",
    "data[0]": "value",
    "start": "2026-09-28",
    "length": 5000,
}

response = requests.get(url, params=params)
response.raise_for_status()
df = pd.DataFrame(response.json()["response"]["data"])

print(df[["series", "series-description", "units"]].drop_duplicates().to_string())