import pandas as pd
import talib
from flask import current_app
from app import db
from app.models import IndicatorValues, StockPrice  
from sqlalchemy.dialects.postgresql import insert

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
    
    result = []
    for name, group in grouped:
        group.loc[:, "rsi"] = talib.RSI(group["close_price"], timeperiod=14)
        group.loc[:, "sma"] = talib.SMA(group["close_price"], timeperiod=20)
        group.loc[:, "momentum"] = talib.MOM(group["close_price"], timeperiod=10)
        group.loc[:, "adx"] = talib.ADX(group["high"], group["low"], group["close_price"], timeperiod=14)
        group.loc[:, "obv"] = talib.OBV(group["close_price"], group["volume"])
        
        result.append(group)
    
    combined_df = pd.concat(result)
    
    combined_df = combined_df.fillna(0)

    combined_df = combined_df.drop_duplicates(subset=['stock_symbol', 'date'], keep='last')

    return combined_df

def insert_or_update_indicator_values(df):
    """Insert new indicator values or update existing ones using PostgreSQL ON CONFLICT."""
    try:
        # Check if DataFrame is empty
        if df.empty:
            current_app.logger.warning("DataFrame is empty, nothing to insert")
            return
            
        # Print some diagnostic information
        current_app.logger.info(f"Preparing to upsert {len(df)} records")
        current_app.logger.info(f"Sample data: {df.head(2).to_dict('records')}")
        
        # Convert DataFrame to a list of dictionaries
        values_list = df[['stock_symbol', 'date', 'rsi', 'sma', 'obv', 'adx', 'momentum']].to_dict('records')
        
        # Create the upsert statement
        stmt = insert(IndicatorValues).values(values_list)
        
        # Define what to do on conflict - update all indicator values
        update_dict = {
            'rsi': stmt.excluded.rsi,
            'sma': stmt.excluded.sma,
            'obv': stmt.excluded.obv,
            'adx': stmt.excluded.adx,
            'momentum': stmt.excluded.momentum
        }
        
        # Create the complete upsert statement with ON CONFLICT behavior
        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=['stock_symbol', 'date'],
            set_=update_dict
        )
        
        # Execute the statement
        result = db.session.execute(upsert_stmt)
        db.session.commit()
        
        # Log the operation results
        current_app.logger.info(f"Inserted {len(values_list)} indicator records successfully.")
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating indicator values: {str(e)}")
        # Print full exception details for debugging
        import traceback
        current_app.logger.error(traceback.format_exc())
        
def process_stock_indicators():
    """Main function to fetch stock data, calculate indicators, and store in DB in batches."""
    stock_data = fetch_stock_data()
    if stock_data is None or stock_data.empty:
        current_app.logger.error("Stock data is empty! Check your StockPrice table.")
        return
    else:
        current_app.logger.info(f"Fetched {len(stock_data)} stock records.")
    if stock_data is not None and not stock_data.empty:
        batch_size = 1000
        total_rows = len(stock_data)
        
        for start in range(0, total_rows, batch_size):
            end = min(start + batch_size, total_rows)
            batch_df = stock_data.iloc[start:end]  
            
            batch_df = calculate_indicators(batch_df)
            
            insert_or_update_indicator_values(batch_df)
            
            current_app.logger.warning(f"Batch {start // batch_size + 1} of {total_rows // batch_size + 1} processed.") 
    else:
        current_app.logger.info("No stock data found!")

