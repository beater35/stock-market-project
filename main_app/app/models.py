from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime

app = Flask(__name__)
db = SQLAlchemy(app)

# Define the model for all the stock prices from 2012 to 2020
class StockPrices(db.Model):
    __tablename__ = 'stock_prices'
    
    id = db.Column(db.Integer, primary_key=True)
    s_no = db.Column(db.Integer)
    symbol = db.Column(db.String(10))
    date = db.Column(db.Date)
    open = db.Column(db.Numeric(10, 2))
    high = db.Column(db.Numeric(10, 2))
    low = db.Column(db.Numeric(10, 2))
    close = db.Column(db.Numeric(10, 2))
    volume = db.Column(db.BigInteger)

# Define the User model
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    # One-to-Many relationship with Stock
    stocks = db.relationship('Stock', backref='user', lazy=True)

# Define the Stock model (this connects the stock to the user)
class Stock(db.Model):
    __tablename__ = 'stock'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock_symbol = db.Column(db.String(10), nullable=False)
    date_purchased = db.Column(db.DateTime, default=datetime.utcnow)
    purchase_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# Don't recreate the stock_prices table
# It's already in PostgreSQL

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock_symbol = db.Column(db.String(10), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # BUY or SELL
    quantity = db.Column(db.Integer, nullable=False)
    price_per_share = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_amount = db.Column(db.Numeric(10, 2), nullable=False)  # New: Amount before tax
    broker_commission_rate = db.Column(db.Numeric(5, 3), nullable=False)  # New: Broker commission rate
    sebon_fee_rate = db.Column(db.Numeric(5, 3), nullable=False)  # New: SEBON fee rate
    total_amount_paid = db.Column(db.Numeric(10, 2), nullable=True)  # After tax and fees for buys
    total_amount_received = db.Column(db.Numeric(10, 2), nullable=True)  # After tax and fees for sells
    profit_or_loss = db.Column(db.Numeric(10, 2), nullable=True)  # Profit or loss when selling stocks
    date = db.Column(db.Date, nullable=False)
    
    def __repr__(self):
        return f"Transaction('{self.stock_symbol}', '{self.transaction_type}', '{self.quantity}')"


class Tax(db.Model):
    __tablename__ = 'taxes'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    broker_commission = db.Column(db.Float, nullable=False)
    sebon_fee = db.Column(db.Float, nullable=False)
    dp_amount = db.Column(db.Float, nullable=False, default=25.00)
    capital_gain_tax = db.Column(db.Float, nullable=True)  # Null for 'BUY'
    
    def __repr__(self):
        return f"Tax('Transaction: {self.transaction_id}', 'Broker Commission: {self.broker_commission}')"
