import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from the parent directory
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
load_dotenv(dotenv_path)

# Database connection parameters
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

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

# Insert data from CSV in batches
def insert_data_from_csv(file_path, batch_size=1000):
    connection = create_connection()
    if connection is None:
        print("Failed to connect to the database.")
        return
    
    cursor = connection.cursor()

    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)

        # Clean the date format and volume data
        df['Date'] = df['Date'].str.split('.').str[0]
        df['Volume'] = df['Vol'].str.replace(",", "").astype(int)
        
        # Drop the unnecessary columns (if any)
        df = df[['S.no', 'Symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume']]

        # Prepare the insert query
        insert_query = '''
        INSERT INTO stock_prices (s_no, symbol, date, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        '''
        
        # Iterate over the DataFrame in batches
        batch_data = []
        for index, row in df.iterrows():
            # Add data to the batch
            batch_data.append((
                row['S.no'], row['Symbol'], row['Date'], row['Open'],
                row['High'], row['Low'], row['Close'], row['Volume']
            ))

            # If batch size is reached, insert into the database
            if len(batch_data) >= batch_size:
                cursor.executemany(insert_query, batch_data)
                connection.commit()  # Commit the transaction
                print(f"{len(batch_data)} rows inserted.")
                batch_data = []  # Clear the batch
        
        # Insert any remaining rows that didn't fill the final batch
        if batch_data:
            cursor.executemany(insert_query, batch_data)
            connection.commit()
            print(f"{len(batch_data)} remaining rows inserted.")

    except Exception as e:
        print(f"Error inserting data: {e}")

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()

# Example usage
if __name__ == "__main__":
    csv_file_path = "/home/beater35/VS code/FYP/archive/archive/OHLC.csv"  # Update with the actual CSV file path
    insert_data_from_csv(csv_file_path)


