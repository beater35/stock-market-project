import pandas as pd
import numpy as np
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
        group.loc[:, "adx"] = talib.ADX(group["high"], group["low"], group["close_price"])
        group.loc[:, "obv"] = talib.OBV(group["close_price"], group["volume"])
        
        result.append(group)
    
    combined_df = pd.concat(result)
    
    combined_df = combined_df.fillna(0)

    combined_df = combined_df.drop_duplicates(subset=['stock_symbol', 'date'], keep='last')

    return combined_df

def insert_or_update_indicator_values(df):
    """Insert new indicator values or update existing ones using PostgreSQL ON CONFLICT."""
    try:
        if df.empty:
            current_app.logger.warning("DataFrame is empty, nothing to insert")
            return
            
        current_app.logger.info(f"Preparing to upsert {len(df)} records")
        current_app.logger.info(f"Sample data: {df.head(2).to_dict('records')}")
        
        values_list = df[['stock_symbol', 'date', 'rsi', 'sma', 'obv', 'adx', 'momentum']].to_dict('records')
        
        stmt = insert(IndicatorValues).values(values_list)
        
        update_dict = {
            'rsi': stmt.excluded.rsi,
            'sma': stmt.excluded.sma,
            'obv': stmt.excluded.obv,
            'adx': stmt.excluded.adx,
            'momentum': stmt.excluded.momentum
        }
        
        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=['stock_symbol', 'date'],
            set_=update_dict
        )
        
        result = db.session.execute(upsert_stmt)
        db.session.commit()
        
        current_app.logger.info(f"Inserted {len(values_list)} indicator records successfully.")
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating indicator values: {str(e)}")
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


import numpy as np
import pandas as pd

def calculate_adx(high, low, close, period=14):

    high = np.array(high, dtype=float)
    low = np.array(low, dtype=float)
    close = np.array(close, dtype=float)
    
    output_length = len(high)
    tr = np.full(output_length, np.nan)
    plus_dm = np.full(output_length, np.nan)
    minus_dm = np.full(output_length, np.nan)
    
    for i in range(1, output_length):
        tr1 = high[i] - low[i]  
        tr2 = abs(high[i] - close[i-1])  
        tr3 = abs(low[i] - close[i-1])  
        tr[i] = max(tr1, tr2, tr3)
        
        up_move = high[i] - high[i-1]
        down_move = low[i-1] - low[i]
        
        if up_move > down_move and up_move > 0:
            plus_dm[i] = up_move
        else:
            plus_dm[i] = 0
            
        if down_move > up_move and down_move > 0:
            minus_dm[i] = down_move
        else:
            minus_dm[i] = 0
    
    tr_series = pd.Series(tr)
    plus_dm_series = pd.Series(plus_dm)
    minus_dm_series = pd.Series(minus_dm)
    
    tr14 = np.full(output_length, np.nan)
    plus_dm14 = np.full(output_length, np.nan)
    minus_dm14 = np.full(output_length, np.nan)
    
    if output_length > period:
        tr14[period] = tr_series[1:period+1].sum()
        plus_dm14[period] = plus_dm_series[1:period+1].sum()
        minus_dm14[period] = minus_dm_series[1:period+1].sum()
    
        for i in range(period+1, output_length):
            tr14[i] = tr14[i-1] - (tr14[i-1] / period) + tr[i]
            plus_dm14[i] = plus_dm14[i-1] - (plus_dm14[i-1] / period) + plus_dm[i]
            minus_dm14[i] = minus_dm14[i-1] - (minus_dm14[i-1] / period) + minus_dm[i]
    
    plus_di = np.full(output_length, np.nan)
    minus_di = np.full(output_length, np.nan)
    
    for i in range(period, output_length):
        if tr14[i] > 0:
            plus_di[i] = 100 * plus_dm14[i] / tr14[i]
            minus_di[i] = 100 * minus_dm14[i] / tr14[i]
    
    dx = np.full(output_length, np.nan)
    for i in range(period, output_length):
        if (plus_di[i] + minus_di[i]) > 0:
            dx[i] = 100 * abs(plus_di[i] - minus_di[i]) / (plus_di[i] + minus_di[i])
    
    adx = np.full(output_length, np.nan)
    
    if output_length > 2 * period:
        adx[2*period-1] = np.mean(dx[period:2*period])
        
        for i in range(2*period, output_length):
            adx[i] = ((adx[i-1] * (period-1)) + dx[i]) / period
    
    return pd.Series(adx)
