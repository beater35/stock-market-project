from datetime import datetime
from app import db
import requests
from bs4 import BeautifulSoup
from app.models import LiveStockPrice, Stock

def web_scrape_live():
    url = "https://eng.merolagani.com/LatestMarket.aspx"
    response = requests.get(url)

    if response.status_code == 200:
        print("Successfully fetched the webpage!")
        soup = BeautifulSoup(response.content, 'html.parser')

        # Scrape the date (static)
        date_element = soup.find('span', {'id': 'ctl00_ContentPlaceHolder1_date'})
        if date_element:
            date_str = date_element.get_text(strip=True).replace("As of ", "").split()[0]  
            date = datetime.strptime(date_str, "%Y/%m/%d").date() 
            print(f"Scraped date: {date}")
        else:
            print("Date not found on the webpage.")
            return []

        # Scrape the current time (using datetime module)
        current_time = datetime.now().time()  # Get current time
        print(f"Current time: {current_time}")

        # Scrape the market table
        table = soup.find('table', {'class': 'table table-hover live-trading sortable'})
        if not table:
            print("Table not found on the webpage.")
            return []

        rows = table.find('tbody').find_all('tr')
        live_data = []

        for row in rows:
            columns = row.find_all('td')
            column_data = [col.get_text(strip=True) if col.get_text(strip=True) else "N/A" for col in columns]

            # Ensure correct number of columns (ignoring last 2)
            if len(column_data) < 8: 
                print(f"Skipping row due to missing data: {column_data}")
                continue

            live_data.append({
                "symbol": column_data[0],  
                "ltp": column_data[1].replace(',', ''),  # Current price (last traded price)
                "volume": column_data[6].replace(',', ''),  # Volume
                "date": date,  # Scraped date
                "time": current_time  # Current time
            })

        return live_data
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return []


def scrape_and_store_live():
    scraped_data = web_scrape_live()

    for data in scraped_data:
        try:
            # Extract the date and time from the scraped data
            date = data.get("date")
            time = data.get("time")
            if not date or not time:
                print("Skipping row due to missing date or time.")
                continue

            # Convert values to the correct type
            symbol = data["symbol"]
            close_price = float(data["ltp"]) if data["ltp"] != "N/A" else None
            volume = int(data["volume"]) if data["volume"] != "N/A" else None

            # Ensure required fields are not missing
            if not (symbol and close_price and volume):
                print(f"Skipping {symbol} due to missing required data.")
                continue

            # Find stock by symbol (not by ID anymore)
            stock = Stock.query.filter_by(symbol=symbol).first()
            if not stock:
                print(f"Stock {symbol} not found in the database. Skipping...")
                continue

            # Check if the live data for the same stock, date, and time already exists
            existing_record = LiveStockPrice.query.filter_by(stock_symbol=symbol, date=date, time=time).first()
            if existing_record:
                print(f"Live data for {symbol} at {date} {time} already exists. Skipping...")
                continue

            # Save the live stock data into the database
            new_live_price = LiveStockPrice(
                stock_symbol=symbol,
                date=date,
                time=time,
                price=close_price,
                volume=volume
            )
            db.session.add(new_live_price)
            print(f"Added live data for {symbol} at {date} {time}.")

        except Exception as e:
            print(f"Error processing {data['symbol']}: {e}")

    db.session.commit()
    print("Live scraping and storage complete!")
