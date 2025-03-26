from flask_migrate import Migrate
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
# from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_ADDRESS')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL_ADDRESS')

# Database Configuration
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

migrate = Migrate(app, db)

logging.basicConfig(level=logging.INFO)

@login_manager.user_loader
def load_user(user_id):
    from app.models import User 
    return User.query.get(int(user_id))

scheduler = BackgroundScheduler()

def process_indicators_after_scrape():
    from app.calculate_indicators import process_stock_indicators  
    with app.app_context():
        process_stock_indicators()

def scrape_stock_data():
    from app.scraper import scrape_and_store 
    
    with app.app_context():  
        now = datetime.now()

        if now.weekday() in [4, 5]:
            print("Market is closed today. Skipping scraping.")
            return
        
        # if now.hour < 15 or (now.hour == 15 and now.minute < 15):
        #     print("Market is still open. Waiting until after 3:15 PM.")
        #     return

        print(f"Running scrape task at {now}...")
        try:
            scrape_and_store()
            print("Scraping completed. Starting indicator calculations...")

            process_indicators_after_scrape()
        except Exception as e:
            print(f"Error during scraping: {e}")

scheduler.add_job(
    scrape_stock_data,
    'interval',
    days=1,
    id="daily_scraper",
    replace_existing=True,
    next_run_time=datetime.now()
)

scheduler.start()

@app.teardown_appcontext
def shutdown_scheduler(exception=None):
    if scheduler.running:
        print("Shutting down scheduler...")
        scheduler.shutdown(wait=False)


from app.routes import *

# Import and start the live market scheduler
from app.live_market.scheduler import start_scheduler
start_scheduler()





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
