import os

class Config:
    SECRET_KEY = 'your-hard-coded-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///your_database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False