from flask import render_template, redirect, url_for, flash, request
from app import app, db, bcrypt
from app.models import User, Stock, Transaction, Tax
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime


# Home page route
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


# Portfolio page route
@app.route('/portfolio')
@login_required
def portfolio():
    # Query to fetch all stock associated with the current user
    stocks = Stock.query.filter_by(user_id=current_user.id).all()
    return render_template('portfolio.html', stocks=stocks)


# Add stock route
@app.route('/buy_stock', methods=['POST'])
@login_required
def buy_stock():
    if request.method == 'POST':
        # Get form data
        stock_symbol = request.form.get('stock_symbol').upper()
        quantity = int(request.form.get('quantity'))
        purchase_price = float(request.form.get('purchase_price'))
        purchase_date = request.form.get('purchase_date')
        user_type = request.form.get('user_type') # Institution or Individual

        # Convert purchase_date from string to datetime object
        purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d')

        # Validate the inputs
        if not stock_symbol or not purchase_price or not quantity or not purchase_date:
            flash('Please fill out all fields.', 'danger')
            return redirect(url_for('portfolio'))
        
        # Calculate transaction amount
        transaction_amount = purchase_price * quantity

        # Create or update stock entry in the stock table
        stock = Stock.query.filter_by(user_id=current_user.id, stock_symbol=stock_symbol).first()

        if stock:
            # Update existing stock entry's total quantity
            stock.quantity += quantity
        else:
            # Create a new stock entry
            stock = Stock(
                user_id=current_user.id, 
                stock_symbol=stock_symbol, 
                date_purchased=purchase_date, 
                purchase_price=purchase_price, 
                quantity=quantity
            )
            db.session.add(stock)
        
        db.session.commit()

        # Record the purchase as a new transaction (FIFO tracking)
        transaction = Transaction(
            user_id=current_user.id,
            stock_symbol=stock_symbol,
            transaction_type='BUY',
            quantity=quantity,
            date=purchase_date,
            transaction_amount=transaction_amount,
            user_type=user_type,
            purchase_price=purchase_price
        )

        db.session.add(transaction)
        db.session.commit() # Commit to generate a transaction ID

        # Now calculate the broker commission and SEBON fee using methods from the Transaction model
        broker_commission = transaction.calculate_broker_commission(transaction_amount)
        sebon_fee = transaction.calculate_sebon_fee(transaction_amount)
        
        # Calculate total amount paid (including DP amount)
        total_amount_paid = transaction.calculate_total_amount_paid(transaction_amount, broker_commission, sebon_fee)

        # Calculate price per share
        price_per_share = total_amount_paid / quantity

        # Calculate the broker commission rate and sebon fee rate
        broker_commission_rate = broker_commission / transaction_amount
        sebon_fee_rate = sebon_fee / transaction_amount

        # Update the transaction with the calculated price per share, total amount paid, sebon fee rate, broker commission rate
        transaction.price_per_share = price_per_share
        transaction.total_amount_paid = total_amount_paid
        transaction.broker_commission_rate = broker_commission_rate
        transaction.sebon_fee_rate = sebon_fee_rate
        db.session.commit()

        # Create a new Tax entry linked to this transaction
        tax = Tax(
            transaction_id=transaction.id,
            broker_commission=broker_commission,
            sebon_fee=sebon_fee,
            dp_amount=25,
            capital_gain_tax=None
        )

        db.session.add(tax)
        db.session.commit()


# Sell stock route
@app.route('sell_stock/<int:stock_id>', methods=['POST'])
@login_required
def sell_stock(stock_id):
    stock = Stock.query.get_or_404(stock_id)
    quantity_to_sell = int(request.form.get('quantity'))

    # Ensure the stock belongs to the current user
    if stock.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('portfolio'))

    # Ensure the user doesn't sell more than they own
    if stock.quantity < quantity_to_sell:
        flash('You cannot sell more than you own.', 'danger')
        return redirect(url_for('portfolio'))

    # Adjust the quantity after selling
    stock.quantity -= quantity_to_sell

    # If no stock left, we remove the record
    if stock.quantity == 0:
        db.session.delete(stock)
    else:
        db.session.add(stock)

    db.session.commit()

    flash(f'Successfully sold {quantity_to_sell} shares of {stock.stock_symbol}.', 'success')
    return redirect(url_for('portfolio'))

# Route for user register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
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
