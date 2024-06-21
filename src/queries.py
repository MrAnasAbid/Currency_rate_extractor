
def currency_code_queries(codes):
    queries_list = []
    new_currency_names = 0
    for _, row in codes.iterrows():
        single_query = f"""
        INSERT OR IGNORE INTO currency_names (currency_code, currency_name)
        VALUES ('{row['currency_code']}', '{row['currency_name']}');
        """
        queries_list.append(single_query)
        new_currency_names += 1
    if new_currency_names > 0:
        print(f"Attempting to insert {new_currency_names} new currency names...")
    else:
        return None
    return queries_list

def currency_rate_queries(conversion_rates):
    queries_list = []
    new_currency_rates = 0

    for _, row in conversion_rates.iterrows():
        single_query = f"""
        INSERT OR IGNORE INTO currency_rates (currency_code, rate, date)
        VALUES ('{row['currency_code']}', '{row['rate']}', '{row['date']}');
        """
        queries_list.append(single_query)
        new_currency_rates += 1

    if new_currency_rates > 0:
        print(f"Attemping to insert {new_currency_rates} new currency rates...")
    else:
        return None

    return queries_list

def create_tables_queries():
    create_currency_names = """
    CREATE TABLE IF NOT EXISTS currency_names (
        currency_code TEXT PRIMARY KEY,
        currency_name TEXT
    );
    """
    create_currency_rates = """
    CREATE TABLE IF NOT EXISTS currency_rates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        currency_code TEXT,
        rate REAL,
        date TEXT,
        FOREIGN KEY (currency_code) REFERENCES currency_names(currency_code),
        UNIQUE (currency_code, date)
    );
    """
    return [create_currency_names, create_currency_rates]