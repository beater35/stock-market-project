from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime
from flask_login import UserMixin
from app import db

# Import the calculation methods for taxes from calculations.py
from .calculations import (
    calculate_broker_commission, calculate_sebon_fee, calculate_capital_gain_tax,
    calculate_total_amount_paid, calculate_total_amount_received
)



# Define the model for all the stock prices from 2012 to 2020
class StockPrices(db.Model, UserMixin):
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
    user_type = db.Column(db.String(15), nullable=False)

    # One-to-Many relationship with Stock
    stocks = db.relationship('Stock', backref='user', lazy=True)
    # One-to-Many relationship with Transaction
    transactions = db.relationship('Transaction', backref='user', lazy=True)



# Define the Stock model (this connects the stock to the user)
class Stock(db.Model):
    __tablename__ = 'stock'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock_symbol = db.Column(db.String(10), nullable=False)
    date_purchased = db.Column(db.DateTime, default=datetime.utcnow)
    purchase_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)



# Transaction Table
class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock_symbol = db.Column(db.String(10), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # BUY or SELL
    quantity = db.Column(db.Integer, nullable=False)
    price_per_share = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    transaction_amount = db.Column(db.Numeric(10, 2), nullable=False)  # New: Amount before tax
    broker_commission_rate = db.Column(db.Numeric(5, 3), nullable=False)  # New: Broker commission rate
    sebon_fee_rate = db.Column(db.Numeric(5, 3), nullable=False)  # New: SEBON fee rate
    total_amount_paid = db.Column(db.Numeric(10, 2), nullable=True)  # After tax and fees for buys
    total_amount_received = db.Column(db.Numeric(10, 2), nullable=True)  # After tax and fees for sells
    profit_or_loss = db.Column(db.Numeric(10, 2), nullable=True)  # Profit or loss when selling stocks
    capital_gain_tax = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_price = db.Column(db.Numeric(10, 2), nullable=False)

    # One-to-one relationship with Tax
    tax = db.relationship("Tax", backref="transaction", uselist=False)

    def __repr__(self):
        return f"Transaction('{self.stock_symbol}', '{self.transaction_type}', '{self.quantity}')"


    # Methods to calculate commission, fees, and taxes
    def calculate_broker_commission(self):
        """Calculate broker commission using the helper function."""
        return calculate_broker_commission(self.transaction_amount)

    def calculate_sebon_fee(self):
        """Calculate SEBON fee using the helper function."""
        return calculate_sebon_fee(self.transaction_amount)

    def calculate_capital_gain_tax(self):
        """Calculate capital gain tax based on profit/loss, user type, and holding period."""
        
        # Find the matching BUY transaction for this stock symbol and user
        buy_transaction = Transaction.query.filter_by(
            user_id=self.user_id, 
            stock_symbol=self.stock_symbol, 
            transaction_type='BUY'
        ).first()
        
        if not buy_transaction:
            return 0  # If no corresponding BUY transaction, no tax can be calculated
        
        purchase_date = buy_transaction.date  # Use the date of the "BUY" transaction as purchase_date
        sell_date = self.date  # Use the current transaction's date as the sell_date (which is the sell date)

        return calculate_capital_gain_tax(
            profit_or_loss=self.profit_or_loss,
            user_type=self.user_type,
            purchase_date=purchase_date,
            sell_date=sell_date
        )

    def calculate_total_amount_paid(self):
        """Calculate total amount paid after broker commission and SEBON fee for BUY transactions."""
        broker_commission = self.calculate_broker_commission()
        sebon_fee = self.calculate_sebon_fee()
        return calculate_total_amount_paid(self.transaction_amount, broker_commission, sebon_fee)

    def calculate_total_amount_received(self):
        """Calculate total amount received after broker commission, SEBON fee, and capital gain tax for SELL transactions."""
        broker_commission = self.calculate_broker_commission()
        sebon_fee = self.calculate_sebon_fee()
        capital_gain_tax = self.calculate_capital_gain_tax()
        return calculate_total_amount_received(self.transaction_amount, broker_commission, sebon_fee, capital_gain_tax)



# Tax Table
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
