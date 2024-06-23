import os
import sys
import requests
import pandas as pd
import paramiko
import sqlite3
import matplotlib.pyplot as plt
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
from src.constants import BASE_CURRENCY
from src.utils import load_env_variables, SQLiteConnection
from src.queries import create_tables_queries, currency_code_queries, currency_rate_queries

def process_currency_data(currency_df, currency_code=None, currency_name=None):
    """
    Process the currency DataFrame to prepare it for plotting.
    
    Parameters:
    - currency_df: DataFrame containing currency data.
    - currency_code: Specific currency code to filter the data.
    - currency_name: Specific currency name to filter the data.
    
    Returns:
    - complete_df: Processed DataFrame with filled values and additional columns.
    - currency_code: The currency code used for filtering.
    - currency_name: The currency name used for filtering.
    """
    if currency_code is None and currency_name is None:
        raise ValueError("You must specify either currency_code or currency_name")
    if currency_code is not None and currency_name is not None:
        raise ValueError("You must specify either currency_code or currency_name, not both")

    if currency_code is not None:
        currency_df_filtered = currency_df.loc[currency_df["currency_code"] == currency_code].copy()
    if currency_name is not None:
        currency_df_filtered = currency_df.loc[currency_df["currency_name"].str.contains(currency_name)].copy()

    currency_name = currency_df_filtered["currency_name"].iloc[0]
    currency_code = currency_df_filtered["currency_code"].iloc[0]
    currency_df_filtered["date_standard_format"] = pd.to_datetime(currency_df_filtered["date"])
    currency_df_filtered["in_dollars"] = 1 / currency_df_filtered["rate"]

    first_date = currency_df_filtered["date_standard_format"].min()
    last_date = currency_df_filtered["date_standard_format"].max()

    # Create a complete DataFrame with date range
    complete_dates = pd.date_range(start=first_date, end=last_date, freq="D")
    complete_df = pd.DataFrame({"date_standard_format": complete_dates})
    complete_df = complete_df.merge(currency_df_filtered, on="date_standard_format", how="left")
    complete_df["in_dollars"] = complete_df["in_dollars"].ffill()
    complete_df["date_natural_format"] = complete_df["date_standard_format"].dt.strftime("%d/%m/%Y")
    complete_df["date"] = complete_df["date_standard_format"].dt.strftime("%d %B %Y")
    complete_df[["currency_code", "currency_name", "rate"]] = complete_df[["currency_code", "currency_name", "rate"]].ffill()

    return complete_df, currency_code, currency_name

def plot_currency_evolution(complete_df, currency_code = None, currency_name = None):
    """
    Plot the evolution of the value of a currency in USD over time.
    
    Parameters:
    - complete_df: DataFrame containing processed currency data.
    - currency_code: The currency code used for filtering.
    - currency_name: The currency name used for filtering.
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    
    if currency_code is None and currency_name is None:
        raise ValueError("You must specify either currency_code or currency_name")
    if currency_code is not None and currency_name is not None:
        raise ValueError("You must specify either currency_code or currency_name, not both")

    if currency_code is not None:
        complete_df_filtered = complete_df.loc[complete_df["currency_code"] == currency_code].copy()
    if currency_name is not None:
        complete_df_filtered = complete_df.loc[complete_df["currency_name"].str.contains(currency_name)].copy()

    currency_code, currency_name = complete_df_filtered["currency_code"].iloc[0], complete_df_filtered["currency_name"].iloc[0]

    complete_df_filtered.plot(x="date_natural_format", y="in_dollars", title=f"{currency_code} ({currency_name}) value in USD",
                     ylabel="USD", xlabel="date_natural_format", rot=45, marker="o", legend=False, ax=ax)
    
    # Set the xticks to be every day
    ax.set_xticks(range(0, len(complete_df_filtered), 1))
    # Set xtick labels to be the date in natural format
    ax.set_xticklabels(complete_df_filtered["date_natural_format"], rotation=60)
    ax.grid(True)
    ax.set_xlabel("")
    ax.set_ylabel("Value in USD ($)")
    ax.set_title(f"Evolving value of {currency_code} ({currency_name}) value in USD")
    return fig, ax, currency_code, currency_name

if __name__ == "__main__":
    print("Loading environment variables...")
    api_key, ssh_host, ssh_port, ssh_user, local_ssh_key, remote_ssh_key, private_remote_key, remote_db_path, verbose = load_env_variables()

    fetch_data_query = '''
    SELECT currency_rates.Currency_Code, currency_names.Currency_Name, currency_rates.Rate, currency_rates.date
    FROM currency_rates
    JOIN currency_names
    ON currency_rates.Currency_Code = currency_names.Currency_Code
    '''
    
    conn = sqlite3.connect('data/currency_rates.db')
    c = conn.cursor()

    data = pd.read_sql_query(fetch_data_query, conn)
    print("Data loaded successfully...")
    print(data.head())

    currency_df = pd.read_sql_query(fetch_data_query, conn)
    currency_df["rate"] = currency_df["rate"].astype(float)
    print("Data loaded successfully...")
    print("Looks like this:")
    print(currency_df.head())

    concatenated_df = pd.DataFrame()
    n_currency_codes = len(currency_df["currency_code"].unique())
    for i, currency_code in enumerate(list(currency_df["currency_code"].unique())[:100]):
        print(f"{i+1} / {n_currency_codes} Processing currency {currency_code}")
        df, _, _ = process_currency_data(currency_df, currency_code=currency_code)
        concatenated_df = pd.concat([concatenated_df, df], axis=0)

    print(concatenated_df)
    fig, ax, currency_code, _ = plot_currency_evolution(concatenated_df, currency_code="EUR")
    if not os.path.exists(ROOT / "figures"):
        os.makedirs(ROOT / "figures")
    figure_path = Path(ROOT / "figures" / f"currency_evolution_EUR.png")
    fig.savefig(figure_path)