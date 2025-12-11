import pandas as pd
import sqlite3
import os
import re

SQL_FILE_PATH = os.path.join(os.path.dirname(__file__), "isro-missions.sql")

def load_data():
    """
    Reads the SQL file, executes it in an in-memory SQLite database,
    and returns a clean Pandas DataFrame.
    """
    if not os.path.exists(SQL_FILE_PATH):
        raise FileNotFoundError(f"SQL file not found at {SQL_FILE_PATH}")

    # Create in-memory DB
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # Read SQL script
    with open(SQL_FILE_PATH, 'r') as f:
        sql_script = f.read()

    # Execute SQL script
    # The script might contain multiple statements.
    try:
        cursor.executescript(sql_script)
    except sqlite3.Error as e:
        print(f"Error executing SQL script: {e}")
        # Build logic to handle if the script isn't immediately compatible with sqlite3 executescript
        # But looking at the file content, it seems standard standard SQL.
        return pd.DataFrame() # Return empty on failure for now

    # Load into DataFrame
    query = "SELECT * FROM isro_space_missions"
    try:
        df = pd.read_sql_query(query, conn)
    except Exception as e:
         print(f"Error reading from DB: {e}")
         return pd.DataFrame()

    conn.close()

    return preprocess_data(df)

def preprocess_data(df):
    """
    Cleans data and performs feature engineering.
    """
    if df.empty:
        return df
    
    # 1. Cleaning
    # Handle missing values
    # For numerical columns, fill with mean/median (if any exist and are null). 
    # For this dataset, columns seem to be strings mostly or non-null.
    # We will check for empty strings or None.
    
    # Fill categorical nulls with mode
    for col in ['orbit_type', 'launch_vehicle', 'application', 'outcome', 'launch_site']:
        if col in df.columns:
            mode_val = df[col].mode()[0]
            df[col] = df[col].fillna(mode_val)

    # 2. Feature Engineering
    # Create Success_Flag
    # Outcome column values need inspection. Usually 'Launch successful' or 'Launch unsuccessful'.
    # Normalize string to handle case sensitivity
    df['outcome_norm'] = df['outcome'].str.lower().str.strip()
    df['Success_Flag'] = df['outcome_norm'].apply(lambda x: 1 if 'success' in x and 'unsuccessful' not in x else 0)
    
    # Date Parsing
    df['launch_date'] = pd.to_datetime(df['launch_date'])
    df['Year'] = df['launch_date'].dt.year
    df['Month'] = df['launch_date'].dt.month_name()
    
    # Cumulative Launches
    df = df.sort_values(by='launch_date')
    df['Cumulative_Launches'] = range(1, len(df) + 1)
    
    # Drop intermediate columns if needed, but keeping them for now is fine.
    
    return df

if __name__ == "__main__":
    # Test loading
    df = load_data()
    print(df.head())
    print(df.info())
    print(df['Success_Flag'].value_counts())
