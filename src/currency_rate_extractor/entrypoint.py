import logging
import os
import sqlite3
import pandas as pd
from pathlib import Path
import plotly.offline as offline
from currency_rate_extractor.transform_and_plot import process_currency_data, plot_currency_evolution

from currency_rate_extractor.extract_and_load import fetch_and_merge_exchange_rates
from currency_rate_extractor.queries import create_tables_queries, currency_code_queries, currency_rate_queries

ROOT = os.getenv("ROOT",)

logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed output
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("currency_rate_extractor.log"),
        logging.StreamHandler()
    ]
)

def main():
    api_key = os.getenv('EXCHANGE_RATE_API_KEY', None)
    if not api_key:
        logging.error("API key is not set. Please set the EXCHANGE_RATE_API_KEY environment variable.")
        exit(1)
    logging.info("Main function: Fetching and merging exchange rates...")
    fetch_and_merge_exchange_rates(api_key)

    load_and_join_data_query = '''
    SELECT currency_rates.Currency_Code, currency_names.Currency_Name, currency_rates.Rate, currency_rates.date
    FROM currency_rates
    JOIN currency_names
    ON currency_rates.Currency_Code = currency_names.Currency_Code
    '''
    conn = sqlite3.connect('data/currency_rates.db')
    c = conn.cursor()

    data = pd.read_sql_query(load_and_join_data_query, conn)
    logging.info("Data loaded successfully...")
    print(data.head())

    currency_df = pd.read_sql_query(load_and_join_data_query, conn)
    currency_df["rate"] = currency_df["rate"].astype(float)
    logging.info("Data loaded successfully...")
    logging.info("Looks like this:")
    print(currency_df.head())

    concatenated_df = pd.DataFrame()
    n_currency_codes = len(currency_df["currency_code"].unique())
    for i, currency_code in enumerate(list(currency_df["currency_code"].unique())):
        logging.info(f"{i+1} / {n_currency_codes} Processing currency {currency_code}")
        df, _, _ = process_currency_data(currency_df, currency_code=currency_code)
        concatenated_df = pd.concat([concatenated_df, df], axis=0)

    print(concatenated_df)
    fig, currency_code, _ = plot_currency_evolution(concatenated_df, currency_code="EUR")
    if not os.path.exists(Path(ROOT, "figures")):
        os.makedirs(Path(ROOT, "figures"))
    figure_path = (Path(ROOT, "figures", f"currency_evolution_EURO.html"))
    offline.plot(fig, filename=str(figure_path))

if __name__ == "__main__":
    main()