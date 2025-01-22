from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime
from flask_login import UserMixin
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    preferences = db.Column(db.JSON, nullable=True)

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    sector = db.Column(db.String(50), nullable=True)

class StockPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    open_price = db.Column(db.Float, nullable=False)
    close_price = db.Column(db.Float, nullable=False)
    high = db.Column(db.Float, nullable=False)
    low = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Integer, nullable=False)

# class Indicator(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
#     indicator_name = db.Column(db.String(50), nullable=False)
#     calculated_value = db.Column(db.Float, nullable=False)
#     date = db.Column(db.Date, nullable=False)
#     strength = db.Column(db.String(50), nullable=True)
#     tooltip = db.Column(db.String(255), nullable=True)

class UserPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    indicator_combination = db.Column(db.JSON, nullable=False)  # JSON to store combinations
    weightage = db.Column(db.JSON, nullable=False)  # JSON to store weightage for each combination
    user = db.relationship('User', backref='preferences', lazy=True)
