import os
import sys
import requests
import pandas as pd
import paramiko
import matplotlib.pyplot as plt
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
from src.constants import BASE_CURRENCY
from src.utils import load_env_variables, SQLiteConnection
from src.queries import create_tables_queries, currency_code_queries, currency_rate_queries

if __name__ == '__main__':
    # Load environment variables
    api_key, ssh_host, ssh_port, ssh_user, local_ssh_key, remote_ssh_key, private_remote_key, remote_db_path, verbose = load_env_variables()

    print(f"api_key: {api_key}")
    print(f"ssh_host: {ssh_host}")
    print(f"ssh_port: {ssh_port}")
    print(f"ssh_user: {ssh_user}")
    print(f"local_ssh_key: {local_ssh_key}")
    print(f"remote_ssh_key: {remote_ssh_key}")
    print(f"private_remote_key: {private_remote_key}")
    print(f"remote_db_path: {remote_db_path}")
    print(f"verbose: {verbose}")

    # sqlite_connection.execute_sqlite_commands_on_remote("SELECT * FROM currency_names;", verbose=True)