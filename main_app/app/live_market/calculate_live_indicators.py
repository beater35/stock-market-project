import datetime
import talib
import pandas as pd
from sqlalchemy import func
from app import db
from app.models import StockPrice, LiveStockPrice, LiveIndicatorValue

# Number of historical days to fetch (14 for RSI, 30 for SMA)
HISTORICAL_DAYS = 40  

def fetch_historical_data(stock_symbol):
    """Fetch last 30 days of historical data from stock_price table."""
    cutoff_date = datetime.date.today() - datetime.timedelta(days=HISTORICAL_DAYS)
    return db.session.query(StockPrice).filter(
        StockPrice.stock_symbol == stock_symbol,
        StockPrice.date >= cutoff_date
    ).order_by(StockPrice.date).all()

def fetch_live_data(stock_symbol):
    """Fetch latest live stock price from live_stock_price table."""
    return db.session.query(LiveStockPrice).filter(
        LiveStockPrice.stock_symbol == stock_symbol
    ).order_by(LiveStockPrice.date.desc(), LiveStockPrice.time.desc()).first()

def calculate_rsi(prices, period=14):
    """Calculate RSI using TA-Lib."""
    return talib.RSI(prices, timeperiod=period)[-1]

def calculate_sma(prices, period=20):
    """Calculate Simple Moving Average (SMA) using TA-Lib."""
    return talib.SMA(prices, timeperiod=period)[-1]

def calculate_obv(prices, volumes):
    """Calculate On-Balance Volume (OBV) using TA-Lib."""
    return talib.OBV(prices, volumes)[-1]

def calculate_adx(highs, lows, closes, period=14):
    """Calculate Average Directional Index (ADX) using TA-Lib."""
    return talib.ADX(highs, lows, closes, timeperiod=period)[-1]

def calculate_momentum(prices, period=10):
    """Calculate Momentum using TA-Lib."""
    return talib.MOM(prices, timeperiod=period)[-1]

def store_live_indicator(stock_symbol, indicator_name, value):
    """Store calculated indicator value in live_indicator_value table."""
    live_data = fetch_live_data(stock_symbol)
    if not live_data:
        print(f"No live data found for {stock_symbol}, skipping...")
        return

    # Check if an entry already exists for this stock, date, time, and indicator
    existing_entry = LiveIndicatorValue.query.filter_by(
        stock_symbol=stock_symbol,
        date=live_data.date,
        time=live_data.time,
        indicator_name=indicator_name
    ).first()

    if existing_entry:
        # Update the existing value instead of creating a new one
        existing_entry.value = value
        print(f"Updated {indicator_name} for {stock_symbol} at {live_data.date} {live_data.time}")
    else:
        # Create a new entry if one doesn't exist
        new_entry = LiveIndicatorValue(
            stock_symbol=stock_symbol,
            date=live_data.date,
            time=live_data.time,
            indicator_name=indicator_name,
            value=value
        )
        db.session.add(new_entry)
        print(f"Added {indicator_name} for {stock_symbol} at {live_data.date} {live_data.time}")

    db.session.commit()

def process_stock(stock_symbol):
    """Fetch data, calculate indicators, and store results."""
    historical_data = fetch_historical_data(stock_symbol)
    if not historical_data:
        print(f"No historical data found for {stock_symbol}, skipping...")
        return

    # Convert historical data to Pandas DataFrame
    df = pd.DataFrame({
        'date': [d.date for d in historical_data],
        'close': [d.close_price for d in historical_data],
        'high': [d.high for d in historical_data],
        'low': [d.low for d in historical_data],
        'volume': [d.volume for d in historical_data]
    }).set_index('date')

    # Compute indicators using TA-Lib
    rsi = calculate_rsi(df['close'])
    sma = calculate_sma(df['close'])
    obv = calculate_obv(df['close'], df['volume'])
    adx = calculate_adx(df['high'], df['low'], df['close'])
    momentum = calculate_momentum(df['close'])

    # Store calculated indicators
    store_live_indicator(stock_symbol, 'RSI', rsi)
    store_live_indicator(stock_symbol, 'SMA', sma)
    store_live_indicator(stock_symbol, 'OBV', obv)
    store_live_indicator(stock_symbol, 'ADX', adx)
    store_live_indicator(stock_symbol, 'Momentum', momentum)

def update_live_indicators():
    """Main function to update live indicator values for all stocks."""
    stock_symbols = db.session.query(StockPrice.stock_symbol).distinct().all()
    stock_symbols = [s[0] for s in stock_symbols]  # Extract symbols from query result

    for symbol in stock_symbols:
        process_stock(symbol)

if __name__ == "__main__":
    update_live_indicators()