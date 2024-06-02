import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('EXCHANGE_RATE_API_KEY')


# Request from the documentation of the website GET https://v6.exchangerate-api.com/v6/YOUR-API-KEY/history/USD/YEAR/MONTH/DAY

date = "2021/01/01"
#url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/EUR/GBP/5.24"
url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
#url = f"https://v6.exchangerate-api.com/v6/{api_key}/history/USD/{date}"

req = requests.get(url)
print(req.content)