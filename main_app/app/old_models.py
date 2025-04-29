from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime
from flask_login import UserMixin
from app import db

from .calculations import (
    calculate_broker_commission, calculate_sebon_fee, calculate_capital_gain_tax,
    calculate_total_amount_paid, calculate_total_amount_received
)



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



class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(15), nullable=False)

    stocks = db.relationship('Stock', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)



class Stock(db.Model):
    __tablename__ = 'stock'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock_symbol = db.Column(db.String(10), nullable=False)
    date_purchased = db.Column(db.DateTime, default=datetime.utcnow)
    purchase_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock_symbol = db.Column(db.String(10), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  
    quantity = db.Column(db.Integer, nullable=False)
    price_per_share = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    transaction_amount = db.Column(db.Numeric(10, 2), nullable=False)  
    broker_commission_rate = db.Column(db.Numeric(5, 3), nullable=False)  
    sebon_fee_rate = db.Column(db.Numeric(5, 3), nullable=False)  
    total_amount_paid = db.Column(db.Numeric(10, 2), nullable=True) 
    total_amount_received = db.Column(db.Numeric(10, 2), nullable=True)  
    profit_or_loss = db.Column(db.Numeric(10, 2), nullable=True) 
    capital_gain_tax = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_price = db.Column(db.Numeric(10, 2), nullable=False)

    tax = db.relationship("Tax", backref="transaction", uselist=False)

    def __repr__(self):
        return f"Transaction('{self.stock_symbol}', '{self.transaction_type}', '{self.quantity}')"


    def calculate_broker_commission(self):
        """Calculate broker commission using the helper function."""
        return calculate_broker_commission(self.transaction_amount)

    def calculate_sebon_fee(self):
        """Calculate SEBON fee using the helper function."""
        return calculate_sebon_fee(self.transaction_amount)

    def calculate_capital_gain_tax(self):
        """Calculate capital gain tax based on profit/loss, user type, and holding period."""
        
        buy_transaction = Transaction.query.filter_by(
            user_id=self.user_id, 
            stock_symbol=self.stock_symbol, 
            transaction_type='BUY'
        ).first()
        
        if not buy_transaction:
            return 0  
        
        purchase_date = buy_transaction.date  
        sell_date = self.date  

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



class Tax(db.Model):
    __tablename__ = 'taxes'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    broker_commission = db.Column(db.Float, nullable=False)
    sebon_fee = db.Column(db.Float, nullable=False)
    dp_amount = db.Column(db.Float, nullable=False, default=25.00)
    capital_gain_tax = db.Column(db.Float, nullable=True)  
    
    def __repr__(self):
        return f"Tax('Transaction: {self.transaction_id}', 'Broker Commission: {self.broker_commission}')"
