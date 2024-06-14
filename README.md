# Currency Exchange Rate Scraper

This project is for practice purposes, it fetches the latest exchange rates from an API and updates a SQLite database with the retrieved data. It runs daily using GitHub Actions.

## Steps

1. **Fetch Data**:
   - The script retrieves the latest exchange rates and currency codes from the API.

2. **Merge and Save**:
   - The fetched data is merged and saved into a SQLite database.

This process is currently automated using GitHub Actions. Future plans include integrating with Apache Airflow for more advanced scheduling and deployment.