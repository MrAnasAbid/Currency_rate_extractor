import sqlite3
import pandas as pd
# Create a sqlite3 database

conn = sqlite3.connect('data/currency_rates.db')
c = conn.cursor()

query = """
SELECT *
FROM currency_rates
ORDER BY rate DESC
"""
data = pd.read_sql_query(query, conn)
print(data)