from pathlib import Path
import sqlite3

def show_schema(db_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query the sqlite_master table to get the schema of all tables
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
    
    # Fetch all results
    tables = cursor.fetchall()
    
    # Print the schema for each table
    for table in tables:
        print(table[0])
    
    # Close the connection
    conn.close()

# Example usage
if __name__ == "__main__":
    db_path = 'data/currency_rates.db'  # Replace with the path to your SQLite database
    show_schema(db_path)