## Project Goal
* Develop an **ELT** (Extract, Load, Transform) pipeline to fetch, process, and store daily currency rates.
* Automate the pipeline using **GitHub Actions** for daily updates.
  
## Data Source
* Exchange Rate API: Provides daily currency rates.
* URL : https://www.exchangerate-api.com/

## Main Tools
![Tools](https://github.com/MrAnasAbid/Currency_rate_extractor/assets/115592120/f9a24e8b-1cad-4e28-bc06-c7a46f7a9dd4)
* **Python** : Handles data processing and extraction via pandas and requests.
* **Sqlite3** : Used as a lightweight database for storing extracted currency rates.
* **Github Actions** : Automates the ELT pipeline, ensuring regular updates to the Sqlite database.

## Workflow Overview
### 1. Extract
* File: **src/extract_and_load.py**
* Task: Extract daily currency rates and codes from the Exchange Rate API.
* Output: Data stored in pandas DataFrames.
### 2. Load
* File: **src/extract_and_load.py**
* Task: Load the extracted data into an SQLite database (currency_rates.db).
* Database Operations: Insert new values or ignore existing ones using SQL queries.
  
![Database_schema](https://github.com/MrAnasAbid/Currency_rate_extractor/assets/115592120/f869ed1c-5beb-41db-8135-5de21fdc2ee3)
### 3. Transform
* File: **src/transform_and_plot.py**
* Task: Transform the data by joining tables, parsing dates, and filling missing values.
### 4. Plot Data (Optional step)
* File: **src/transform_and_plot.py**
* Task: Plot the evolution of specific currency rates over time (e.g., EUR).
* Output: Generate and save visualizations of currency rate trends.

## Automation
* **GitHub Actions**: Automate the entire ETL pipeline to run daily, ensuring the database is updated with the latest currency rates, an artifact with a sample plot is generated (evolution of EURO currency rates)

## Improvements
* The current database is hosted in this GitHub repo (data/currency_rates.db) which isn't ideal. The next step includes hosting it on a virtual machine (WIP, branch SSH_VM).
* Create and deploy a dashboard (with Dash) to visualize more detailed information about the data.
* Enhance code readability and robustness (pylint and pytest)

## How to Use
* Clone the repository
* Install dependencies using pipenv install
* Run the two scripts (extract_and_load.py and transform_and_plot.py).
* Ensure you have the database (data/currency_rates.db) from the repository, as missing this will result in incomplete records.

## Contributing
Feel free to contribute to this project! If you have questions, feedback, or would like to report issues, please reach out:
- **Email:** m.abid.anas@gmail.com
- **LinkedIn:** [Anas Abid](https://www.linkedin.com/in/abidanas/)
