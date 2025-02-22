import os
import sqlite3
import pandas as pd
import plotly.offline as offline
from pathlib import Path
from dotenv import load_dotenv

from currency_rate_extractor.transform_and_plot import process_currency_data, plot_currency_evolution
from currency_rate_extractor.extract_and_load import fetch_and_merge_exchange_rates
from currency_rate_extractor.queries import create_tables_queries, currency_code_queries, currency_rate_queries

from currency_rate_extractor.custom_logging import get_classic_logger

logger = get_classic_logger()

load_dotenv()

ROOT = os.getenv("ROOT")
PATH_TO_DB = Path("data/currency_rates.db")
PATH_TO_FIGURE = Path("figures", "currency_evolution_EURO.html")



def main():
    # Check if the API key is set
    api_key = os.getenv('EXCHANGE_RATE_API_KEY', None)
    if api_key is None:
        raise ValueError("API key is not set. Please set the EXCHANGE_RATE_API_KEY environment variable.")
    
    # 1 - Fetch the Data from the API
    logger.info("Main function: Fetching and merging exchange rates...")
    fetch_and_merge_exchange_rates(api_key)

    load_and_join_data_query = '''
    SELECT currency_rates.Currency_Code, currency_names.Currency_Name, currency_rates.Rate, currency_rates.date
    FROM currency_rates
    JOIN currency_names
    ON currency_rates.Currency_Code = currency_names.Currency_Code
    '''
    conn = sqlite3.connect(Path(ROOT, PATH_TO_DB))
    c = conn.cursor()


    currency_df = pd.read_sql_query(load_and_join_data_query, conn)
    currency_df["rate"] = currency_df["rate"].astype(float)
    logger.info("Data loaded successfully...")
    print(currency_df.head())

    concatenated_df = pd.DataFrame()
    n_currency_codes = len(currency_df["currency_code"].unique())
    for i, currency_code in enumerate(list(currency_df["currency_code"].unique())):
        logger.info(f"{i+1} / {n_currency_codes} Processing currency {currency_code}")

        df, _, _ = process_currency_data(currency_df, currency_code=currency_code)
        concatenated_df = pd.concat([concatenated_df, df], axis=0)

    logger.info("Successfully processed all currency codes, plotting currency evolution...")

    # Plot currency evolution
    fig, currency_code, _ = plot_currency_evolution(concatenated_df, currency_code="EUR")
    # Ensure the figures directory exists
    figure_dir = Path(ROOT, "figures")
    figure_dir.mkdir(parents=True, exist_ok=True)
    # Save the figure
    figure_path = Path(ROOT, PATH_TO_FIGURE)
    offline.plot(fig, filename=str(figure_path), auto_open=False)
    logger.info(f"Figure saved at {figure_path}")

if __name__ == "__main__":
    main()
