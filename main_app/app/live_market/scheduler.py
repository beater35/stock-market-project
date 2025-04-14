import logging
from apscheduler.schedulers.background import BackgroundScheduler
from .fetcher import scrape_and_store_live
from .calculate_live_indicators import update_live_indicators
from datetime import datetime, timedelta
from app import db
from app.models import LiveStockPrice, LiveIndicatorValue
from app import app
from pytz import timezone



# Setting up the logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

def scheduled_live_update():
    """Fetch live stock data and then calculate & store live indicators."""
    now = datetime.now()
    day_of_week = now.weekday()

    now = datetime.now()
    if now.hour < 11 or now.hour >= 15:  # Stop after 3:00 PM
        print("Market is closed. Stopping live updates.")
        return
    
    if day_of_week == 4 or day_of_week == 5:  # Friday (4) or Saturday (5)
        print("Market is closed (Friday or Saturday). Stopping live updates.")
        return

    with app.app_context():
        # scrape_and_store_live()  # Scrape & store live market data
        # update_live_indicators()  # Calculate indicators after data is updated
        return

def cleanup_old_data():
    """Deletes live stock prices and indicator values older than 10 days."""
    cutoff_date = datetime.now() - timedelta(days=10)

    # Delete old stock prices
    db.session.query(LiveStockPrice).filter(LiveStockPrice.date < cutoff_date).delete()

    # Delete old indicator values
    db.session.query(LiveIndicatorValue).filter(LiveIndicatorValue.date < cutoff_date).delete()

    db.session.commit()
    logging.info(f"Deleted live stock and indicator data older than {cutoff_date.date()}")

# Function to start the scheduler
def start_scheduler():
    scheduler = BackgroundScheduler()

    # Get the current time once
    current_time = datetime.now()
    
    # Only start immediately if within allowed hours and weekdays
    next_run = current_time if (11 <= current_time.hour <= 15 and current_time.weekday() in range(5)) else None

    # Schedule live data updates every minute (10 AM - 3 PM, Sun-Thu)
    scheduler.add_job(
        scheduled_live_update,  
        'cron', 
        day_of_week='sun,mon,tue,wed,thu',  
        hour="11,12,13,14",  
        minute='*/5',  
        id='live_data_update',
        next_run_time=next_run,
        timezone=timezone('Asia/Kathmandu')
    )

    # Schedule cleanup job to run daily at 3 AM
    scheduler.add_job(
        cleanup_old_data,
        'cron',
        hour=3,  
        minute=0,  
        id='cleanup_old_data',
        # next_run_time=next_run
    )
    
    # Start the scheduler
    scheduler.start()

    # Log the scheduler's status
    if 11 <= current_time.hour < 15 and current_time.weekday() in range(5):  
        logging.info("Scheduler started: fetching live market data & updating indicators every minute (10 AM - 3 PM).")
    else:
        logging.info("Scheduler initialized, but current time is outside the scheduled range.")

    logging.debug("Scheduler background process started at %s", current_time)

