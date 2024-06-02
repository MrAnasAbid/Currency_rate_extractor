import sqlite3
import pandas as pd
# Create a sqlite3 database

conn = sqlite3.connect('data/currency_rates.db')
c = conn.cursor()

query = """
SELECT *
FROM currency
"""
data = pd.read_sql_query(query, conn)
print(data)