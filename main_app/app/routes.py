from flask import jsonify, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from app import app, db, bcrypt  
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from app.models import User, Stock, IndicatorValues
# from app.email_service import send_reset_email, s


# Home route
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


# About route
@app.route('/about')
def about():
    return render_template('aboutme.html')


# Login route
@app.route('/login')
def login():
    return render_template('login.html')


# Core page route
@app.route('/core')
def core():
    return render_template('core.html')


from flask import jsonify
from datetime import date
from app import db
from app.models import IndicatorValues, Stock

@app.route('/api/companies', methods=['GET'])
def get_companies():
    companies = Stock.query.order_by(Stock.symbol).all()
    company_data = []

    for company in companies:
        latest_indicator = (
            IndicatorValues.query
            .filter_by(stock_symbol=company.symbol)
            .order_by(IndicatorValues.date.desc())  # Get the latest entry
            .first()
        )

        if latest_indicator:
            signals = {
                "RSI": "Buy" if latest_indicator.rsi < 30 else "Sell" if latest_indicator.rsi > 70 else "Hold",
                "ADX": "Strong Trend" if latest_indicator.adx > 25 else "Weak Trend",
                "Momentum": "Buy" if latest_indicator.momentum > 0 else "Sell",
                "SMA": "Buy" if latest_indicator.sma > latest_indicator.rsi else "Sell",  # Example logic
                "OBV": "Buy" if latest_indicator.obv > 0 else "Sell"
            }

            company_data.append({
                "symbol": company.symbol,
                "date": latest_indicator.date.strftime("%Y-%m-%d"),
                "signals": signals
            })

    return jsonify(company_data)



# Indicator values from database route
@app.route('/api/indicators', methods=['GET'])
def get_latest_indicators():
    # Get the latest date for each stock symbol
    latest_dates = db.session.query(
        IndicatorValues.stock_symbol,
        func.max(IndicatorValues.date).label("latest_date")
    ).group_by(IndicatorValues.stock_symbol).subquery()

    # Get the latest indicator values for each stock symbol
    latest_indicators = db.session.query(
        IndicatorValues.stock_symbol,
        IndicatorValues.date,
        IndicatorValues.rsi,
        IndicatorValues.sma,
        IndicatorValues.obv,
        IndicatorValues.adx,
        IndicatorValues.momentum
    ).join(latest_dates, 
        (IndicatorValues.stock_symbol == latest_dates.c.stock_symbol) &
        (IndicatorValues.date == latest_dates.c.latest_date)
    ).all()

    # Convert query result to JSON format
    indicators_data = [
        {
            "symbol": ind.stock_symbol,
            "date": ind.date.strftime('%Y-%m-%d'),
            "RSI": ind.rsi,
            "SMA": ind.sma,
            "OBV": ind.obv,
            "ADX": ind.adx,
            "Momentum": ind.momentum
        }
        for ind in latest_indicators
    ]

    return jsonify(indicators_data)


# Company page route
@app.route('/company')
def company():
    return render_template('company.html')
# @app.route('/company/<symbol>')
# def company_page(symbol):
#     company = Stock.query.filter_by(symbol=symbol).first()
#     if not company:
#         return "Company not found", 404
#     return render_template('company.html', company=company)


# Register route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        
        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in or use a different email.", "danger")
            return redirect(url_for("register"))
        
        # Check if the username already exists
        existing_user_username = User.query.filter_by(username=username).first()
        if existing_user_username:
            flash("Username already taken. Please choose a different one.", "danger")
            return redirect(url_for("register"))
        
        # Hash the password and create a new user
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(username=username, email=email, password_hash=hashed_password)
        
        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)  # Automatically log the user in after registration
            flash("Registration successful! You are now logged in.", "success")
            return redirect(url_for("home"))
        except IntegrityError:
            db.session.rollback()
            flash("There was an error registering the user.", "danger")
            return redirect(url_for("register"))

    return render_template("login.html")


# Route to handle login logic (POST)
@app.route('/login_route', methods=['GET', 'POST'])
def login_route():
    if current_user.is_authenticated:
        return redirect(url_for('home'))  

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash('You have been logged in!', 'success')
            return redirect(url_for('home')) 
        else:
            flash('Login failed. Check your email and password.', 'danger')

    return redirect(url_for('login'))  


# Forgot password route
# @app.route('/forgot-password', methods=['GET', 'POST'])
# def forgot_password():
#     if request.method == 'POST':
#         email = request.form['email']
        
#         # Add logic to check if the email exists and send a password reset email
#         user = User.query.filter_by(email=email).first()
#         if user:
#             # Send reset link to the user's email
#             send_reset_email(user)
#             flash('A reset link has been sent to your email.', 'success')
#         else:
#             flash('No account found with that email address.', 'danger')
        
#         return redirect(url_for('forgot_password'))
    
#     return render_template('forgot-password.html')


# Reset password route
# @app.route('/reset-password/<token>', methods=['GET', 'POST'])
# def reset_password(token):
#     try:
#         email = s.loads(token, salt='password-reset-salt', max_age=3600)  # Token expires after 1 hour
#     except Exception:
#         flash('The password reset link is invalid or has expired.', 'danger')
#         return redirect(url_for('forgot_password'))
    
#     user = User.query.filter_by(email=email).first()
#     if not user:
#         flash('Invalid or expired token.', 'danger')
#         return redirect(url_for('forgot_password'))
    
#     if request.method == 'POST':
#         password = request.form['password']
#         user.password = bcrypt.generate_password_hash(password).decode('utf-8')
#         db.session.commit()
#         flash('Your password has been updated!', 'success')
#         return redirect(url_for('login_route'))
    
#     return render_template('reset-password.html')


# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))



if __name__ == "__main__":
    app.run(debug=True)
