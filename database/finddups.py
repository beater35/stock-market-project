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

def find_duplicates():
    connection = create_connection()
    if connection is None:
        print("Failed to connect to the database.")
        return

    cursor = connection.cursor()

    query = """
        SELECT stock_symbol, date, COUNT(*) 
        FROM stock_price 
        GROUP BY stock_symbol, date 
        HAVING COUNT(*) > 1;
    """

    try:
        cursor.execute(query)
        duplicates = cursor.fetchall()

        if duplicates:
            print("Duplicate records found:")
            for row in duplicates:
                print(f"Stock Symbol: {row[0]}, Date: {row[1]}, Count: {row[2]}")
        else:
            print("No duplicate records found.")

    except Exception as e:
        print(f"Error executing query: {e}")

    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    find_duplicates()
