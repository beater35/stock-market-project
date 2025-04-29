import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
load_dotenv(dotenv_path)

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

BATCH_SIZE = 5000  

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

def insert_historical_data_from_csv(csv_file_path):
    connection = create_connection()
    if connection is None:
        print("Failed to connect to the database.")
        return
    
    cursor = connection.cursor()

    cursor.execute("SELECT symbol FROM stock;")
    valid_symbols = {row[0] for row in cursor.fetchall()}

    cursor.execute("SELECT stock_symbol, date FROM stock_price;")
    existing_records = {(row[0], row[1]) for row in cursor.fetchall()} 

    insert_query = '''
        INSERT INTO stock_price (stock_symbol, date, open_price, high, low, close_price, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
    '''

    try:
        df = pd.read_csv(csv_file_path)

        df = df.rename(columns={
            "Symbol": "stock_symbol",
            "Date": "date",
            "Open": "open_price",
            "High": "high",
            "Low": "low",
            "Close": "close_price",
            "Vol": "volume"
        })

        df["date"] = df["date"].str.replace(".csv", "", regex=False)
        df["date"] = pd.to_datetime(df["date"])  

        df["open_price"] = df["open_price"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close_price"] = df["close_price"].astype(float)

        df["volume"] = df["volume"].astype(str).str.replace(",", "").astype(int)

        df = df[df["stock_symbol"].isin(valid_symbols)]

        df = df.drop_duplicates(subset=["stock_symbol", "date"])

        data_tuples = [
            (row.stock_symbol, row.date, row.open_price, row.high, row.low, row.close_price, row.volume)
            for row in df.itertuples(index=False)
            if (row.stock_symbol, row.date) not in existing_records  
        ]

        total_records = len(data_tuples)
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
    csv_file_path = "/home/beater35/VS code/FYP/archive/archive/OHLC.csv"  
    insert_historical_data_from_csv(csv_file_path)
