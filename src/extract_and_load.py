import os
import sys
import requests
import pandas as pd
import paramiko
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
from src.constants import BASE_CURRENCY
from src.utils import load_env_variables, SQLiteConnection
from src.queries import create_tables_queries, currency_code_queries, currency_rate_queries
#from src.test_vm import execute_sqlite_commands_on_remote

def fetch_and_merge_exchange_rates(sqlite_connection: SQLiteConnection) -> None:
    try:
        # Extraction Phase
        # 1 - Request the latest exchange rates and extract the json data
        print("Fetching the latest exchange rates...")
        url_currency_rates = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{BASE_CURRENCY}"
        req_currency = requests.get(url_currency_rates)
        req_currency.raise_for_status()  # Raise HTTPError for bad responses
        data = req_currency.json()

        # 2 - Transform the data into a pandas DataFrame
        print("Transforming the data into a pandas DataFrame...")
        conversion_rates = pd.DataFrame(data['conversion_rates'].items(), columns=['currency_code', 'rate'])
        conversion_rates["date"] = data["time_last_update_utc"].split(" 00:")[0]
        print("Snippet of the currency codes and rates:")
        print(conversion_rates.head())

        # 3 - Extract currency codes and names
        print("Extracting currency codes and names...")
        url_currency_codes = f'https://v6.exchangerate-api.com/v6/{api_key}/codes'
        req_codes = requests.get(url_currency_codes)
        req_codes.raise_for_status()  # Raise HTTPError for bad responses
        data_code = req_codes.json()

        # 4 - Transform the data into a pandas DataFrame
        codes = pd.DataFrame(data_code["supported_codes"], columns=["currency_code", "currency_name"])
        print("Snippet of the currency codes and names:")
        print(codes.head())

        # Load Phase
        # 1 - Generate SQL queries to insert data into remote SQLite database
        create_tables_if_not_exists = create_tables_queries()
        insert_or_ignore_into_currency_codes = currency_code_queries(codes)
        insert_or_ignore_into_currency_rate = currency_rate_queries(conversion_rates)

        # 2 - Execute SQL commands on remote SQLite database (by calling sqlite_conncetion object)
        stdout, stderr = sqlite_connection.execute_sqlite_commands_on_remote(create_tables_if_not_exists, verbose=False)
        stdout, stderr = sqlite_connection.execute_sqlite_commands_on_remote(insert_or_ignore_into_currency_codes, verbose=False)
        stdout, stderr = sqlite_connection.execute_sqlite_commands_on_remote(insert_or_ignore_into_currency_rate, verbose=False)
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during API request: {e}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    print("Loading environment variables...")
    api_key, ssh_host, ssh_port, ssh_user, local_ssh_key, remote_ssh_key, private_remote_key, remote_db_path, verbose = load_env_variables()

    # VERY bad practice incoming
    if verbose == "REMOTE":
        local_ssh_key = remote_ssh_key

    print("Initializing SQLite connection with the environment variables...")
    sqlite_connection = SQLiteConnection(ssh_host, ssh_port, ssh_user, local_ssh_key, remote_db_path)

    print("Main function: Fetching and merging exchange rates...")
    fetch_and_merge_exchange_rates(sqlite_connection)
