from flask import render_template, redirect, url_for, flash, request
from app import app, db, bcrypt
from app.models import User, Stock, Transaction, Tax
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/portfolio')
@login_required
def portfolio():
    stocks = Stock.query.filter_by(user_id=current_user.id).all()
    return render_template('portfolio.html', stocks=stocks)


@app.route('/buy_stock', methods=['POST'])
@login_required
def buy_stock():
    if request.method == 'POST':
        stock_symbol = request.form.get('stock_symbol').upper()
        quantity = int(request.form.get('quantity'))
        purchase_price = float(request.form.get('purchase_price'))
        purchase_date = request.form.get('purchase_date')

        purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d')

        if not stock_symbol or not purchase_price or not quantity or not purchase_date:
            flash('Please fill out all fields.', 'danger')
            return redirect(url_for('portfolio'))
        
        transaction_amount = purchase_price * quantity

        stock = Stock.query.filter_by(user_id=current_user.id, stock_symbol=stock_symbol).first()

        if stock:
            stock.quantity += quantity
        else:
            stock = Stock(
                user_id=current_user.id, 
                stock_symbol=stock_symbol, 
                date_purchased=purchase_date, 
                purchase_price=purchase_price, 
                quantity=quantity
            )
            db.session.add(stock)
        
        db.session.commit()

        transaction = Transaction(
            user_id=current_user.id,
            stock_symbol=stock_symbol,
            transaction_type='BUY',
            quantity=quantity,
            date=purchase_date,
            transaction_amount=transaction_amount,
            transaction_price=purchase_price
        )

        db.session.add(transaction)
        db.session.commit() 

        broker_commission = transaction.calculate_broker_commission(transaction_amount)
        sebon_fee = transaction.calculate_sebon_fee(transaction_amount)
        
        total_amount_paid = transaction.calculate_total_amount_paid(transaction_amount, broker_commission, sebon_fee)

        price_per_share = total_amount_paid / quantity

        broker_commission_rate = broker_commission / transaction_amount
        sebon_fee_rate = sebon_fee / transaction_amount

        transaction.price_per_share = price_per_share
        transaction.total_amount_paid = total_amount_paid
        transaction.broker_commission_rate = broker_commission_rate
        transaction.sebon_fee_rate = sebon_fee_rate
        db.session.commit()

        tax = Tax(
            transaction_id=transaction.id,
            broker_commission=broker_commission,
            sebon_fee=sebon_fee,
            dp_amount=25,
            capital_gain_tax=None
        )

        db.session.add(tax)
        db.session.commit()


@app.route('/sell_stock', methods=['POST'])
@login_required
def sell_stock():
    if request.method == 'POST':
        stock_symbol = request.form.get('stock_symbol').upper()
        quantity_to_sell = int(request.form.get('quantity'))
        sell_price = float(request.form.get('sell_price'))
        sell_date = request.form.get('sell_date')

        user_type = current_user.user_type

        sell_date = datetime.strptime(sell_date, '%Y-%m-%d')

        if not stock_symbol or not sell_price or not quantity_to_sell or not sell_date:
            flash('Please fill out all fields.', 'danger')
            return redirect(url_for('portfolio'))
        
        stock = Stock.query.filter_by(user_id=current_user.id, stock_symbol=stock_symbol).first

        if not stock or stock.quantity < quantity_to_sell:
            flash('You do now own enough shares to sell.', 'danger')
            return redirect(url_for('portfolio'))
        
        remaining_quantity_to_sell = quantity_to_sell
        buy_transactions = Transaction.query.filter_by(
            user_id=current_user.id,
            stock_symbol=stock_symbol,
            transaction_type='BUY'
        ).order_by(Transaction.date).all()

        total_profit = 0
        short_term_profit = 0
        long_term_profit = 0

        for transaction in buy_transactions:
            if remaining_quantity_to_sell == 0:
                break

            if transaction.quantity > remaining_quantity_to_sell:
                transaction_profit = (sell_price - transaction.purchase_price) * remaining_quantity_to_sell
                total_profit += transaction_profit

                holding_period = (sell_date - transaction.date).days
                if holding_period < 365:
                    short_term_profit += transaction_profit
                else:
                    long_term_profit += transaction_profit

                remaining_quantity_to_sell = 0
            else:
                transaction_profit = (sell_price - transaction.purchase_price) * transaction.quantity
                total_profit += transaction_profit

                holding_period = (sell_date - transaction.date).days
                if holding_period < 365:
                    short_term_profit += transaction_profit
                else:
                    long_term_profit += transaction_profit

                remaining_quantity_to_sell -= transaction.quantity

        stock.quantity -= quantity_to_sell
        if stock.quantity == 0:
            db.session.delete(stock)
        else:
            db.session.add(stock)

        db.session.commit()

        transaction_amount = sell_price * quantity_to_sell

        sell_transaction = Transaction(
            user_id=current_user.id,
            stock_symbol=stock_symbol,
            transaction_type='SELL',
            quantity=quantity_to_sell,
            date=sell_date,
            transaction_amount=transaction_amount,
            profit_or_loss=total_profit,
            transaction_price=sell_price
        )

        db.session.add(sell_transaction)
        db.session.commit()

        broker_commission = sell_transaction.calculate_broker_commission(transaction_amount)
        sebon_fee = sell_transaction.calculate_sebon_fee(transaction_amount)

        capital_gain_tax = sell_transaction.calculate_capital_gain_tax(total_profit, user_type, short_term_profit, long_term_profit)

        total_amount_received = sell_transaction.calculate_total_amount_received(transaction_amount, broker_commission, sebon_fee, capital_gain_tax)

        broker_commission_rate = broker_commission / transaction_amount
        sebon_fee_rate = sebon_fee / transaction_amount

        sell_transaction.broker_commission_rate = broker_commission_rate
        sell_transaction.sebon_fee_rate = sebon_fee_rate
        sell_transaction.capital_gain_tax = capital_gain_tax
        sell_transaction.total_amount_received = total_amount_received
        db.session.commit()

        tax = Tax(
            transaction_id=sell_transaction.id,
            broker_commission=broker_commission,
            sebon_fee=sebon_fee,
            dp_amount=25,
            capital_gain_tax=capital_gain_tax
        )

        db.session.add(tax)
        db.session.commit()


# Route for user register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        user_type = request.form.get('user_type').lower()
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password, user_type=user_type)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Your account has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html')


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
    return render_template('login.html')


# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))
