import os
import sys
import requests
import pandas as pd
import sqlite3
from dotenv import load_dotenv
from pathlib import Path

# ROOT is above the folder this code is in
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
from src.constants import BASE_CURRENCY

"""
Main script to fetch the latest exchange rates and store them in a SQLite database
Currency rates & codes are stored in two separate tables
For safety, we import the codes every time we fetch the rates
This script is to be ran daily
"""

# Load environment variables from a .env file
def fetch_and_merge_exchange_rates():
    load_dotenv()
    api_key = os.getenv('EXCHANGE_RATE_API_KEY')

    # Request the latest exchange rates and extract the json data
    url_currency_rates = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{BASE_CURRENCY}"
    req_currency = requests.get(url_currency_rates)
    data = req_currency.json()

    # Transform the data into a pandas DataFrame
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

if __name__ == '__main__':
    fetch_and_merge_exchange_rates()
