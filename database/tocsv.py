import psycopg2
import csv
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
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

# Function to export data to CSV
def export_to_csv():
    connection = create_connection()
    if connection is None:
        print("Failed to connect to the database.")
        return

    cursor = connection.cursor()

    # Query to select all records from stock_price table
    query = """
    SELECT stock_symbol, date, open_price, close_price, high, low, volume
    FROM stock_price;
    """

    try:
        cursor.execute(query)
        # Fetch all rows
        rows = cursor.fetchall()

        # Define the CSV file path
        csv_file_path = 'stock_price_data_export.csv'

        # Write the data to a CSV file
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write the header
            writer.writerow(['Symbol', 'Date', 'Open Price', 'Close Price', 'High', 'Low', 'Volume'])
            # Write the rows
            writer.writerows(rows)

        print(f"Data exported successfully to {csv_file_path}.")

    except Exception as e:
        print(f"Error exporting data to CSV: {e}")

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()

# Call the export function
if __name__ == "__main__":
    export_to_csv()
