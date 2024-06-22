import os
import sys
import requests
import pandas as pd
import sqlite3
from pathlib import Path

# ROOT is above the folder this code is in
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
from src.constants import BASE_CURRENCY
from src.utils import load_env_variables
"""
Main script to fetch the latest exchange rates and store them in a SQLite database
Currency rates & codes are stored in two separate tables
For safety, we import the codes every time we fetch the rates
This script is to be ran daily
"""

# Load environment variables from a .env file
api_key, vm_ip, verbose, ssh_host, ssh_port, ssh_user, ssh_key, remote_db_path, remote_ssh = load_env_variables()

def fetch_and_merge_exchange_rates():
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
    new_currency_names = 0
    for _, row in codes.iterrows():
        c.execute("""
        INSERT OR IGNORE INTO currency_names (currency_code, currency_name)
        VALUES (?, ?)
        """, (row['currency_code'], row['currency_name']))
        new_currency_names += c.rowcount
    if new_currency_names == 0:
        print("No new currency names were added")

    # Insert or update currency rates
    new_currency_rates = 0
    for _, row in conversion_rates.iterrows():
        c.execute("""
        INSERT OR IGNORE INTO currency_rates (currency_code, rate, date)
        VALUES (?, ?, ?)
        """, (row['currency_code'], row['rate'], row['date']))
        new_currency_rates += c.rowcount
    if new_currency_rates == 0:
        print("No new currency rates were fetched")
    else:
        print(f"👍 Inserted {len(conversion_rates)} exchange rates for the date of: {conversion_rates['date'].unique()[0]}")
    
    print(f"Current size of the currency_rates table: {c.execute('SELECT COUNT(*) FROM currency_rates').fetchone()[0]} rows")
    print(f"Current table spans {c.execute('SELECT COUNT(DISTINCT date) FROM currency_rates').fetchone()[0]} days")

    # Commit the transaction
    conn.commit()

    # Close the connection
    conn.close()

if __name__ == '__main__':
    fetch_and_merge_exchange_rates()
