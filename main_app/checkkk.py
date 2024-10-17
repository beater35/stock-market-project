import psycopg2
import os

# Load the DATABASE_URL
database_url = 'postgresql://postgres:SuccessIsWithin35@localhost/stock_data'

# Parse the components of the URL
if not database_url:
    raise ValueError("No DATABASE_URL found.")

try:
    # Connect to the PostgreSQL server
    conn = psycopg2.connect(database_url)
    print("Connection successful!")
except psycopg2.OperationalError as e:
    print("Unable to connect to the database.")
    print(e)
finally:
    if conn:
        conn.close()
