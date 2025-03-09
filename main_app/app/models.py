from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime
from flask_login import UserMixin
from app import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def is_active(self):
        return True 
    
    def get_id(self):
        return str(self.id) 


class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    sector = db.Column(db.String(50), nullable=True)


class StockPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_symbol = db.Column(db.String(10), db.ForeignKey('stock.symbol'), nullable=False)    
    date = db.Column(db.Date, nullable=False)
    open_price = db.Column(db.Float, nullable=False)
    close_price = db.Column(db.Float, nullable=False)
    high = db.Column(db.Float, nullable=False)
    low = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Integer, nullable=False)


class IndicatorValues(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_symbol = db.Column(db.String(10), db.ForeignKey('stock.symbol', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    rsi = db.Column(db.Float)
    sma = db.Column(db.Float)
    obv = db.Column(db.BigInteger) 
    adx = db.Column(db.Float)
    momentum = db.Column(db.Float)

    __table_args__ = (db.UniqueConstraint('stock_symbol', 'date', name='unique_stock_date'),)

    def __repr__(self):
        return f"<IndicatorValues {self.stock_symbol} {self.date}>"


class IndicatorEffectiveness(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_symbol = db.Column(db.String(10), db.ForeignKey('stock.symbol', ondelete='CASCADE'), nullable=False)
    indicator_name = db.Column(db.String(10), nullable=False)
    best_buy = db.Column(db.Float) 
    best_sell = db.Column(db.Float)
    win_rate = db.Column(db.Float) 
    avg_profit = db.Column(db.Float) 
    sample_size = db.Column(db.Integer) 
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('stock_symbol', 'indicator_name', name='unique_stock_indicator'),)

    def __repr__(self):
        return f"<IndicatorEffectiveness {self.stock_symbol} {self.indicator_name}>"


class UserPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    indicator_combination = db.Column(db.JSON, nullable=False)
    weightage = db.Column(db.JSON, nullable=False)  
    user = db.relationship('User', backref='preferences', lazy=True)
