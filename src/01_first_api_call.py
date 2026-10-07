import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# 1. Read the secret key from the .env file
load_dotenv()
API_KEY = os.getenv("EIA_API_KEY")

# 2. The address of the "counter" and what we want from it
URL = "https://api.eia.gov/v2/petroleum/pri/spt/data/"

params = {
    "api_key": API_KEY,
    "frequency": "daily",
    "data[0]": "value",
    "facets[series][]": ["RBRTE", "RWTC"],   # Brent, WTI
    "start": "2024-01-01",
    "sort[0][column]": "period",
    "sort[0][direction]": "asc",
    "length": 5000,
}

# 3. Send the request
response = requests.get(URL, params=params)
print("Status code:", response.status_code)

# 4. Open the stack of papers (JSON) and find the rows
data = response.json()
rows = data["response"]["data"]
df = pd.DataFrame(rows)
print(df.head())
print(df.columns.tolist())

# 5. Fix the data types: dates as dates, prices as numbers
df["period"] = pd.to_datetime(df["period"])
df["value"] = pd.to_numeric(df["value"])

# 6. Reshape: one row per date, one column per oil
prices = df.pivot(index="period", columns="series", values="value")
print(prices.tail())

# 7. Draw and save the chart
prices.plot(figsize=(10, 5), title="Brent vs WTI crude oil price ($/barrel)")
plt.ylabel("$ per barrel")
plt.savefig("docs/brent_wti.png")
plt.show()

# 8. Spread = Brent minus WTI
prices["spread"] = prices["RBRTE"] - prices["RWTC"]

# 9. Summary numbers: average, minimum, maximum, etc.
print("\n--- Spread summary ---")
print(prices["spread"].describe())

# 10. The 10 widest-spread days
print("\n--- 10 widest spread days ---")
print(prices["spread"].sort_values(ascending=False).head(10))

# 11. The 10 biggest one-day price moves for WTI (in percent)
prices["wti_daily_change_pct"] = prices["RWTC"].pct_change() * 100
print("\n--- 10 biggest WTI daily moves (%) ---")
biggest_moves = prices["wti_daily_change_pct"].abs().sort_values(ascending=False).head(10)
print(prices.loc[biggest_moves.index, ["RWTC", "wti_daily_change_pct"]])

# 12. Chart the spread on its own
prices["spread"].plot(figsize=(10, 4), title="Brent minus WTI spread ($/barrel)")
plt.ylabel("$ per barrel")
plt.savefig("docs/brent_wti_spread.png")
plt.show()