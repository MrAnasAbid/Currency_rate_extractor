# Currency Exchange Rate Scraper
This project uses GitHub Actions to fetch data from a currency exchange rates API, process it, and insert it into a SQLite3 database. The workflow is scheduled to run daily.

## Steps
- Fetch Data: Retrieve the latest exchange rates and currency codes from the API.
- Insert Data: Merge the fetched data and save it into a SQLite database.
