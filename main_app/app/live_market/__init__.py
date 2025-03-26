# Import the function to start the scheduler from scheduler.py
from .scheduler import start_scheduler

# Start the live market data fetching scheduler as soon as the live_market module is imported
start_scheduler()

# If needed, you can add any additional setup or configurations specific to live_market here.
# For example, logging, error handling, etc.
