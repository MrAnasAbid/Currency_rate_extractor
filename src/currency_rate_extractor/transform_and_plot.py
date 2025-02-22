import os
import pandas as pd
import sqlite3
import plotly.graph_objects as go
import plotly.offline as offline

from plotly.subplots import make_subplots
from pathlib import Path
from typing import List, Tuple

from dotenv import load_dotenv
from currency_rate_extractor.custom_logging import get_classic_logger

logger = get_classic_logger()

load_dotenv()

ROOT = os.getenv("ROOT")
PATH_TO_DB = Path("data/currency_rates.db")

def process_currency_data(currency_df:pd.DataFrame, 
                          currency_code:str=None, 
                          currency_name:str=None) -> Tuple[pd.DataFrame, str, str]:
    """
    Process the currency DataFrame to prepare it for plotting.
    Method mainly contains date parsing and rate conversion to USD.
    
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

def plot_currency_evolution(complete_df:pd.DataFrame, 
                            currency_code:str=None, 
                            currency_name:str=None) -> Tuple[None, str, str]:
    """
    Plot the evolution of the value of a currency in USD over time.
    
    Parameters:
    - complete_df: DataFrame containing processed currency data.
    - currency_code: The currency code used for filtering.
    - currency_name: The currency name used for filtering.
    """
    fig = make_subplots(rows=1, cols=1,)
    
    if currency_code is None and currency_name is None:
        raise ValueError("You must specify either currency_code or currency_name")
    if currency_code is not None and currency_name is not None:
        raise ValueError("You must specify either currency_code or currency_name, not both")

    if currency_code is not None:
        complete_df_sliced = complete_df.loc[complete_df["currency_code"] == currency_code].copy()
    if currency_name is not None:
        complete_df_sliced = complete_df.loc[complete_df["currency_name"].str.contains(currency_name)].copy()

    currency_code, currency_name = complete_df_sliced["currency_code"].iloc[0], complete_df_sliced["currency_name"].iloc[0]
    
    fig.add_trace(
        go.Scatter(
            x=complete_df_sliced["date_standard_format"],
            y=complete_df_sliced["in_dollars"],
            mode='lines+markers',
            hoverinfo='text',
            text=[f"{currency} : {value:.3f}$" for currency, value in zip(complete_df_sliced["date_natural_format"], complete_df_sliced["in_dollars"],)],
            name=None,
            showlegend=False
        ),
        row=1,
        col=1
    )

    fig.update_layout( height=500, width=1400, showlegend=True, title=f"{currency_code} ({currency_name}) currency values in USD", title_x = 0.5)
    fig.update_yaxes(title_text="USD ($)", row=1, col=1,)

    return fig, currency_code, currency_name

if __name__ == "__main__":
    
    fetch_data_query = '''
    SELECT currency_rates.Currency_Code, currency_names.Currency_Name, currency_rates.Rate, currency_rates.date
    FROM currency_rates
    JOIN currency_names
    ON currency_rates.Currency_Code = currency_names.Currency_Code
    '''
    
    conn = sqlite3.connect(Path(ROOT, PATH_TO_DB))
    c = conn.cursor()

    data = pd.read_sql_query(fetch_data_query, conn)
    logger.info("Data loaded successfully...")
    print(data.head())

    currency_df = pd.read_sql_query(fetch_data_query, conn)
    currency_df["rate"] = currency_df["rate"].astype(float)
    logger.info("Data loaded successfully...")
    logger.info("Looks like this:")
    print(currency_df.head())

    concatenated_df = pd.DataFrame()
    n_currency_codes = len(currency_df["currency_code"].unique())
    for i, currency_code in enumerate(list(currency_df["currency_code"].unique())):
        logger.info(f"{i+1} / {n_currency_codes} Processing currency {currency_code}")
        df, _, _ = process_currency_data(currency_df, currency_code=currency_code)
        concatenated_df = pd.concat([concatenated_df, df], axis=0)

    print(concatenated_df)
    fig, currency_code, _ = plot_currency_evolution(concatenated_df, currency_code="EUR")
    if not os.path.exists(ROOT / "figures"):
        os.makedirs(ROOT / "figures")
    figure_path = str(Path(ROOT, "figures", f"currency_evolution_EURO.html"))
    offline.plot(fig, filename=figure_path)