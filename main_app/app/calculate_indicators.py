import pandas as pd
import talib
from flask import current_app
from app import db
from app.models import IndicatorValues, StockPrice  

def fetch_stock_data():
    """Fetch stock data from the database and return as a DataFrame."""
    stock_data = StockPrice.query.order_by(StockPrice.stock_symbol, StockPrice.date).all()
    
    if not stock_data:
        return None
    
    df = pd.DataFrame([{ 
        'stock_symbol': stock.stock_symbol,
        'date': stock.date,
        'close_price': stock.close_price,
        'high': stock.high,
        'low': stock.low,
        'volume': stock.volume
    } for stock in stock_data])
    
    return df

def calculate_indicators(df):
    df = df.copy()
    grouped = df.groupby("stock_symbol")
    
    # Calculate indicators for each group
    result = []
    for name, group in grouped:
        group.loc[:, "rsi"] = talib.RSI(group["close_price"], timeperiod=14)
        group.loc[:, "sma"] = talib.SMA(group["close_price"], timeperiod=20)
        group.loc[:, "momentum"] = talib.MOM(group["close_price"], timeperiod=10)
        group.loc[:, "adx"] = talib.ADX(group["high"], group["low"], group["close_price"], timeperiod=14)
        group.loc[:, "obv"] = talib.OBV(group["close_price"], group["volume"])
        result.append(group)
    
    return pd.concat(result)

def insert_indicator_values_batch(df):
    """Insert or update calculated indicator values in the database in batches."""
    try:
        # List to hold new entries
        new_entries = []
        
        for _, row in df.iterrows():
            # Check if the entry already exists
            existing_record = IndicatorValues.query.filter_by(stock_symbol=row["stock_symbol"], date=row["date"]).first()
            
            if not existing_record:
                new_entry = IndicatorValues(
                    stock_symbol=row["stock_symbol"],
                    date=row["date"],
                    rsi=row["rsi"],
                    sma=row["sma"],
                    obv=row["obv"],
                    adx=row["adx"],
                    momentum=row["momentum"]
                )
                new_entries.append(new_entry)
        
        # Bulk insert the new entries
        if new_entries:
            db.session.bulk_save_objects(new_entries)
            db.session.commit()
            current_app.logger.info(f"Inserted {len(new_entries)} indicator values successfully.")
        else:
            current_app.logger.info("No new indicator values to insert.")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error inserting indicator values: {e}")

def process_stock_indicators():
    """Main function to fetch stock data, calculate indicators, and store in DB in batches."""
    stock_data = fetch_stock_data()
    if stock_data is not None and not stock_data.empty:
        # Process in batches of, say, 10,000 rows
        batch_size = 10000
        total_rows = len(stock_data)
        
        for start in range(0, total_rows, batch_size):
            end = min(start + batch_size, total_rows)
            batch_df = stock_data.iloc[start:end]  # Slice the data for the current batch
            
            # Calculate indicators for the current batch
            batch_df = calculate_indicators(batch_df)
            
            # Insert indicator values for the current batch
            insert_indicator_values_batch(batch_df)
            
            # Log the progress
            current_app.logger.info(f"Processed batch {start // batch_size + 1} of {total_rows // batch_size + 1}")
    else:
        current_app.logger.info("No stock data found!")
