import os
import requests
from dotenv import load_dotenv

"""
Script to test the import of the API key & dotenv package
"""

load_dotenv()
api_key = os.getenv('EXCHANGE_RATE_API_KEY')


# Request from the documentation of the website GET https://v6.exchangerate-api.com/v6/YOUR-API-KEY/history/USD/YEAR/MONTH/DAY

url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"

req = requests.get(url)
print(req.content)