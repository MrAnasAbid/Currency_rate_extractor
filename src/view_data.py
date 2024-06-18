import sqlite3
import pandas as pd
"""
This script is for verbosing the data in the currency_rates table & checking if data is being updated daily
"""

conn = sqlite3.connect('data/currency_rates.db')
c = conn.cursor()

query = """
SELECT *
FROM currency_rates
ORDER BY date DESC
"""
data = pd.read_sql_query(query, conn)
print(data)
print(data["date"].unique())