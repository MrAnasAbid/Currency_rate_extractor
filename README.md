## Project Goal
* Develop an **ETL** (Extract, Transform, Load) pipeline to fetch, process, and store daily currency rates.
* Automate the pipeline using **GitHub Actions** for daily updates.

* Create an ETL pipeline to fetch daily currency rates, track changes, and analyze their evolution.

## Data Source
* Exchange Rate API: Provides daily currency rates.
* URL : https://www.exchangerate-api.com/

## Steps
### 1. Extract
* File: *src/extract_and_load.py*
* Task: Extract daily currency rates and codes from the Exchange Rate API.
* Output: Data stored in pandas DataFrames.
### 2. Load
* File: *src/extract_and_load.py*
* Task: Load the extracted data into an SQLite database (currency_rates.db).
* Database Operations: Insert new values or ignore existing ones using SQL queries.
![UI_preview](https://github.com/MrAnasAbid/Currency_rate_extractor/Database_schema.png)
### 3. Transform
* File: *src/transform_and_plot.py*
* Task: Transform the data by joining tables, parsing dates, and filling missing values.
### 4. Plot Data (Optional step)
* File: *src/transform_and_plot.py*
* Task: Plot the evolution of specific currency rates over time (e.g., EUR).
* Output: Generate and save visualizations of currency rate trends.
![UI_preview](https://github.com/MrAnasAbid/Currency_rate_extractor/currency_evolution_EUR.png)

## Automation
* *GitHub Actions*: Automate the entire ETL pipeline to run daily, ensuring the database is updated with the latest currency rates.

## Improvements
* The current database is hosted in this GitHub repo (data/currency_rates.db) which isn't ideal. The next step includes hosting it on a virtual machine (WIP, branch SSH_VM).
* Create and deploy a dashboard (with Dash) to visualize more detailed information about the data.

## How to Use
* Clone the repository
* Install dependencies using pipenv install
* Run the two scripts (extract_and_load.py and transform_and_plot.py).
* Ensure you have the database (data/currency_rates.db) from the repository, as missing this will result in incomplete records.

## Contributing
Feel free to contribute to this project! If you have questions, feedback, or would like to report issues, please reach out:
- **Email:** m.abid.anas@gmail.com
- **LinkedIn:** [Anas Abid](https://www.linkedin.com/in/abidanas/)