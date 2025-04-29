from datetime import datetime
from app import db
import requests
from bs4 import BeautifulSoup

def web_scrape():
    url = "https://eng.merolagani.com/LatestMarket.aspx"
    response = requests.get(url)

    if response.status_code == 200:
        print("Successfully fetched the webpage!")
        soup = BeautifulSoup(response.content, 'html.parser')

        date_element = soup.find('span', {'id': 'ctl00_ContentPlaceHolder1_date'})
        if date_element:
            date_str = date_element.get_text(strip=True).replace("As of ", "").split()[0]  
            date = datetime.strptime(date_str, "%Y/%m/%d").date() 
            print(f"Scraped date: {date}")
        else:
            print("Date not found on the webpage.")
            return []

        table = soup.find('table', {'class': 'table table-hover live-trading sortable'})
        if not table:
            print("Table not found on the webpage.")
            return []

        headers = []
        header_row = table.find('thead')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
        else:
            print("No headers found.")
            return []

        rows = table.find('tbody').find_all('tr')
        table_data = []

        for row in rows:
            columns = row.find_all('td')
            column_data = [col.get_text(strip=True) if col.get_text(strip=True) else "N/A" for col in columns]

            if len(column_data) < 8: 
                print(f"Skipping row due to missing data: {column_data}")
                continue

            table_data.append({
                "symbol": column_data[0],  
                "ltp": column_data[1].replace(',', ''),  
                "percent_change": column_data[2],
                "open": column_data[3].replace(',', ''),
                "high": column_data[4].replace(',', ''),
                "low": column_data[5].replace(',', ''),
                "volume": column_data[6].replace(',', ''),
                "date": date  
            })

        return table_data
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return []



def scrape_and_store():
    from app.models import Stock, StockPrice

    scraped_data = web_scrape()

    for data in scraped_data:
        try:
            date = data.get("date")
            if not date:
                print("Skipping row as the date is missing.")
                continue

            symbol = data["symbol"]
            open_price = float(data["open"]) if data["open"] != "N/A" else None
            high = float(data["high"]) if data["high"] != "N/A" else None
            low = float(data["low"]) if data["low"] != "N/A" else None
            close_price = float(data["ltp"]) if data["ltp"] != "N/A" else None
            volume = int(data["volume"]) if data["volume"] != "N/A" else None

            if not (symbol and open_price and high and low and close_price and volume):
                print(f"Skipping {symbol} due to missing required data.")
                continue

            stock = Stock.query.filter_by(symbol=symbol).first()
            if not stock:
                print(f"Stock {symbol} not found in the database. Skipping...")
                continue

            existing_record = StockPrice.query.filter_by(stock_symbol=symbol, date=date).first()
            if existing_record:
                print(f"Data for {symbol} on {date} already exists. Skipping...")
                continue

            new_price = StockPrice(
                stock_symbol=symbol,
                date=date,
                open_price=open_price,
                close_price=close_price,
                high=high,
                low=low,
                volume=volume
            )
            db.session.add(new_price)
            print(f"Added data for {symbol} on {date}.")

        except Exception as e:
            print(f"Error processing {data['symbol']}: {e}")

    db.session.commit()
    print("Scraping and storage complete!")

