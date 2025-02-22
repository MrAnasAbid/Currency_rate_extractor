import os
import requests
import pandas as pd
import sqlite3
import logging
from pathlib import Path
from dotenv import load_dotenv

from currency_rate_extractor.queries import create_tables_queries, currency_code_queries, currency_rate_queries
from currency_rate_extractor.custom_logging import get_classic_logger


load_dotenv()

ROOT = os.getenv("ROOT")
PATH_TO_DB = Path("data/currency_rates.db")
BASE_CURRENCY = os.getenv("BASE_CURRENCY")
logger = get_classic_logger()

"""Script that fetches data and loads them into 2 DISTINCT tables"""


def fetch_and_merge_exchange_rates(api_key) -> None:
    try:
        # Extract the current day's exchange rates (daily job)
        url_currency_rates = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{BASE_CURRENCY}"
        req_currency = requests.get(url_currency_rates)
        req_currency.raise_for_status()  # Raise HTTPError for bad responses
        data = req_currency.json()

        # Extract currency codes and names (static data, used for safety)
        url_currency_codes = f'https://v6.exchangerate-api.com/v6/{api_key}/codes'
        req_codes = requests.get(url_currency_codes)
        req_codes.raise_for_status()  # Raise HTTPError for bad responses
        data_code = req_codes.json()

        # Transform the conversion rates data into a pandas DataFrame
        conversion_rates = pd.DataFrame(data['conversion_rates'].items(), columns=['currency_code', 'rate'])
        conversion_rates["date"] = data["time_last_update_utc"].split(" 00:")[0]
        logger.info(f"Snippet of currency codes and rates:\n{conversion_rates.head()}")

        # Transform the currency codes data into a pandas DataFrame
        currency_codes_df = pd.DataFrame(data_code["supported_codes"], columns=["currency_code", "currency_name"])
        logger.info(f"Snippet of currency codes and names:\n{currency_codes_df.head()}")

        # Load Phase
        create_tables_if_not_exists = create_tables_queries()
        insert_or_ignore_into_currency_codes = currency_code_queries(currency_codes_df)
        insert_or_ignore_into_currency_rate = currency_rate_queries(conversion_rates)

        conn = sqlite3.connect(str(Path(ROOT, PATH_TO_DB)))
        c = conn.cursor()

        # Execute the SQL queries
        logger.info("Creating tables if they don't exist...")
        for query in create_tables_if_not_exists:
            c.execute(query)

        logger.info("Inserting or updating currency codes in the database...")
        for query in insert_or_ignore_into_currency_codes:
            c.execute(query)

        logger.info("Inserting or updating currency rates in the database...")
        for query in insert_or_ignore_into_currency_rate:
            c.execute(query)

        conn.commit()
        logger.info("Data successfully loaded into the SQLite database.")

    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred during API request: {e}")
    
    except sqlite3.Error as db_error:
        logger.error(f"Database error: {db_error}")
    
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    api_key = os.getenv('EXCHANGE_RATE_API_KEY', None)
    if not api_key:
        logger.error("API key is not set. Please set the EXCHANGE_RATE_API_KEY environment variable.")
        exit(1)
    logger.info("Main function: Fetching and merging exchange rates...")
    fetch_and_merge_exchange_rates(api_key)