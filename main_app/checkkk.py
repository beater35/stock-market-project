import requests
from bs4 import BeautifulSoup

# Step 1: Send a GET request to the webpage
url = "https://eng.merolagani.com/LatestMarket.aspx"
response = requests.get(url)

# Step 2: Check if the request was successful
if response.status_code == 200:
    print("Successfully fetched the webpage!")

    # Step 3: Parse the webpage content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Step 4: Locate the table by its class
    table = soup.find('table', {'class': 'table table-hover live-trading sortable'})
    
    if table:
        print("Table found! Extracting data...\n")
        
        # Step 5: Extract the table headers
        headers = []
        header_row = table.find('thead')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
            print("Headers:", headers)
        else:
            print("No headers found.")
        
        # Step 6: Extract table rows
        rows = table.find('tbody').find_all('tr')  # Assuming rows are in <tbody>

        table_data = []  # To store all rows' data

        for row_index, row in enumerate(rows):
            # Extract all <td> elements
            columns = row.find_all('td')
            column_data = []
            for col in columns:
                # Handle colspan (if any) by repeating the value or leaving blank
                colspan = col.get('colspan')
                text = col.get_text(strip=True) if col.get_text(strip=True) else "N/A"
                if colspan:
                    column_data.extend([text] * int(colspan))  # Repeat value for colspan
                else:
                    column_data.append(text)
            
            # Add row data to table_data
            table_data.append(column_data)
            print(f"Row {row_index}: {column_data}")

        # Print data in alignment with headers
        print("\nFinal Table Data:")
        print(headers)
        for row in table_data:
            print(row)
    else:
        print("Table not found on the webpage.")
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
