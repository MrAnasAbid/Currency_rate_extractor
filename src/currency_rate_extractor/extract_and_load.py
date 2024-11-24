import os
import requests
import pandas as pd
import sqlite3
from pathlib import Path
import logging

from currency_rate_extractor.constants import BASE_CURRENCY, ROOT
from currency_rate_extractor.queries import create_tables_queries, currency_code_queries, currency_rate_queries

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed output
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("currency_rate_extractor.log"),
        logging.StreamHandler()
    ]
)

def fetch_and_merge_exchange_rates(api_key) -> None:
    try:
        # Extraction Phase
        logging.info("Fetching the latest exchange rates...")
        url_currency_rates = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{BASE_CURRENCY}"
        req_currency = requests.get(url_currency_rates)
        req_currency.raise_for_status()  # Raise HTTPError for bad responses
        data = req_currency.json()
        logging.info("Exchange rates fetched successfully.")

        # Transform the data into a pandas DataFrame
        logging.info("Transforming the exchange rates data into a pandas DataFrame...")
        conversion_rates = pd.DataFrame(data['conversion_rates'].items(), columns=['currency_code', 'rate'])
        conversion_rates["date"] = data["time_last_update_utc"].split(" 00:")[0]
        logging.debug(f"Snippet of currency codes and rates:\n{conversion_rates.head()}")

        # Extract currency codes and names
        logging.info("Fetching the currency codes and names...")
        url_currency_codes = f'https://v6.exchangerate-api.com/v6/{api_key}/codes'
        req_codes = requests.get(url_currency_codes)
        req_codes.raise_for_status()  # Raise HTTPError for bad responses
        data_code = req_codes.json()
        logging.info("Currency codes and names fetched successfully.")

        # Transform the data into a pandas DataFrame
        logging.info("Transforming the currency codes data into a pandas DataFrame...")
        codes = pd.DataFrame(data_code["supported_codes"], columns=["currency_code", "currency_name"])
        logging.debug(f"Snippet of currency codes and names:\n{codes.head()}")

        # Load Phase
        logging.info("Preparing SQL queries to insert data into SQLite database...")
        create_tables_if_not_exists = create_tables_queries()
        insert_or_ignore_into_currency_codes = currency_code_queries(codes)
        insert_or_ignore_into_currency_rate = currency_rate_queries(conversion_rates)

        conn = sqlite3.connect('data/currency_rates.db')
        c = conn.cursor()

        # Execute the SQL queries
        logging.info("Creating tables if they don't exist...")
        for query in create_tables_if_not_exists:
            c.execute(query)

        logging.info("Inserting or updating currency codes in the database...")
        for query in insert_or_ignore_into_currency_codes:
            c.execute(query)

        logging.info("Inserting or updating currency rates in the database...")
        for query in insert_or_ignore_into_currency_rate:
            c.execute(query)

        conn.commit()
        logging.info("Data successfully loaded into the SQLite database.")

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred during API request: {e}")
    
    except sqlite3.Error as db_error:
        logging.error(f"Database error: {db_error}")
    
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    api_key = os.getenv('EXCHANGE_RATE_API_KEY', None)
    if not api_key:
        logging.error("API key is not set. Please set the EXCHANGE_RATE_API_KEY environment variable.")
        exit(1)
    logging.info("Main function: Fetching and merging exchange rates...")
    fetch_and_merge_exchange_rates(api_key)