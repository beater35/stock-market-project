from flask_migrate import Migrate
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file in the parent directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

app = Flask(__name__)

# Use environment variables for sensitive info
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Add the user loader function
@login_manager.user_loader
def load_user(user_id):
    from app.models import User  # Import here to avoid circular imports
    return User.query.get(int(user_id))

# Import routes to ensure they are registered with the app
from app import routes