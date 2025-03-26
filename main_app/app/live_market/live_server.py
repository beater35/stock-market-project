# from datetime import datetime
# from apscheduler.schedulers.background import BackgroundScheduler
# from app import db
# from app.models import StockPrice  # Assuming you're storing price data

# class LiveMarketServer:
#     def __init__(self):
#         self.scheduler = BackgroundScheduler()
#         self.scheduler.start()

#     def start_live_market(self):
#         """Function to start the live market process."""
#         # Here, you'd want to check the time (9 AM to 3 PM, Monday to Thursday)
#         self.scheduler.add_job(self.fetch_live_data, 'interval', hours=1)

#     def stop_live_market(self):
#         """Stop the live market process"""
#         self.scheduler.shutdown()

#     def fetch_live_data(self):
#         """Fetch live market data and update the database."""
#         # You will integrate your `fetcher.py` here
#         pass

#     def is_market_open(self):
#         """Check if the market is open (for example, between 10 AM and 3 PM)."""
#         now = datetime.now()
#         if now.weekday() >= 5:  # Friday or Saturday (market closed)
#             return False
#         if now.hour < 10 or now.hour > 15:  # Not market hours (10 AM - 3 PM)
#             return False
#         return True
