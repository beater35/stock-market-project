import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
load_dotenv(dotenv_path)

# Database connection parameters
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Batch size for inserting records
BATCH_SIZE = 5000 

# Connect to PostgreSQL
def create_connection():
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return connection
    except Exception as e:
        print(f"Error: {e}")
        return None

# Function to insert historical data in batches
def insert_historical_data_from_csv(csv_file_path):
    connection = create_connection()
    if connection is None:
        print("Failed to connect to the database.")
        return
    
    cursor = connection.cursor()

    # Get valid stock symbols from database
    cursor.execute("SELECT symbol FROM stock;")
    valid_symbols = {row[0] for row in cursor.fetchall()}

    # Get existing stock price records (symbol + date)
    cursor.execute("SELECT stock_symbol, date FROM stock_price;")
    existing_records = {(row[0], row[1]) for row in cursor.fetchall()}  # Set of tuples

    insert_query = '''
        INSERT INTO stock_price (stock_symbol, date, open_price, high, low, close_price, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    '''

    try:
        # Read CSV with Pandas
        df = pd.read_csv(csv_file_path)

        # Rename columns to match database schema
        df = df.rename(columns={
            "Symbol": "stock_symbol",
            "Date": "date",
            "Open": "open_price",
            "High": "high",
            "Low": "low",
            "Close": "close_price",
            "Volume": "volume"
        })

        # Convert date column
        df["date"] = pd.to_datetime(df["date"])  # Convert to Date format

        # Convert numerical values
        df["open_price"] = df["open_price"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close_price"] = df["close_price"].astype(float)

        # Remove commas from 'volume' and convert to integer
        df["volume"] = df["volume"].astype(str).str.replace(",", "").str.split(".").str[0].astype(int)

        # Exclude 'Percent Change' column (no need to process it)
        if "Percent Change" in df.columns:
            df = df.drop(columns=["Percent Change"])

        # Keep only valid stock symbols
        df = df[df["stock_symbol"].isin(valid_symbols)]

        # Filter out duplicates by checking if (symbol, date) exists
        df = df[~df.set_index(["stock_symbol", "date"]).index.isin(existing_records)]

        # Convert DataFrame to list of tuples
        data_tuples = df[["stock_symbol", "date", "open_price", "high", "low", "close_price", "volume"]].values.tolist()

        # Insert in batches
        total_records = len(data_tuples)
        if total_records == 0:
            print("No new records to insert.")
        else:
            for i in range(0, total_records, BATCH_SIZE):
                batch = data_tuples[i:i + BATCH_SIZE]
                cursor.executemany(insert_query, batch)
                connection.commit()
                print(f"Inserted {min(i + BATCH_SIZE, total_records)} / {total_records} records...")

            print("All records inserted successfully.")

    except Exception as e:
        print(f"Error processing CSV: {e}")

    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    csv_file_path = "/home/beater35/VS code/FYP/archive/csv/NMB.csv"
    insert_historical_data_from_csv(csv_file_path)
