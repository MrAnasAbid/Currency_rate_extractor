import os
import sys
import requests
import pandas as pd
import sqlite3
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.constants import BASE_CURRENCY

# Load environment variables from a .env file
load_dotenv()
api_key = os.getenv('EXCHANGE_RATE_API_KEY')

# Request the latest exchange rates
url_currency_rates = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{BASE_CURRENCY}"
req_currency = requests.get(url_currency_rates)
data = req_currency.json()
conversion_rates = pd.DataFrame(data['conversion_rates'].items(), columns=['currency_code', 'rate'])
conversion_rates["date"] = data["time_last_update_utc"].split(" 00:")[0]

# Extract currency codes and names
url_currency_codes = f'https://v6.exchangerate-api.com/v6/{api_key}/codes'
req_codes = requests.get(url_currency_codes)
data_code = req_codes.json()
codes = pd.DataFrame(data_code["supported_codes"], columns=["currency_code", "currency_name"])

# Connect to the database
conn = sqlite3.connect('data/currency_rates.db')
c = conn.cursor()

# Create tables if they don't exist
c.execute("""
CREATE TABLE IF NOT EXISTS currency_names (
    currency_code TEXT PRIMARY KEY,
    currency_name TEXT
);
""")
c.execute("""
CREATE TABLE IF NOT EXISTS currency_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    currency_code TEXT,
    rate REAL,
    date TEXT,
    FOREIGN KEY (currency_code) REFERENCES currency_names(currency_code),
    UNIQUE (currency_code, date)
);
""")

# Insert currency names (avoid duplicates)
for _, row in codes.iterrows():
    c.execute("""
    INSERT OR IGNORE INTO currency_names (currency_code, currency_name)
    VALUES (?, ?)
    """, (row['currency_code'], row['currency_name']))

# Insert or update currency rates
for _, row in conversion_rates.iterrows():
    c.execute("""
    INSERT INTO currency_rates (currency_code, rate, date)
    VALUES (?, ?, ?)
    ON CONFLICT(currency_code, date) DO UPDATE SET rate=excluded.rate
    """, (row['currency_code'], row['rate'], row['date']))

# Commit the transaction
conn.commit()

# Close the connection
conn.close()
