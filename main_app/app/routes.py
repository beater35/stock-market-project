from flask import jsonify, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from app import app, db, bcrypt  
import math
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from datetime import datetime, timedelta
# from app.email_service import send_reset_email, s
from app.models import User, Stock, IndicatorValues, StockPrice, LiveIndicatorValue, LiveStockPrice


# Live market page route
@app.route('/live-market')
def live_market():
    return render_template('live_market.html')


# Live signals route
@app.route('/api/live-signals')
def get_buy_sell_signals():
    # Get the latest indicator values for each stock
    latest_timestamps = db.session.query(
        LiveIndicatorValue.stock_symbol,
        func.max(LiveIndicatorValue.date).label('max_date')
    ).group_by(LiveIndicatorValue.stock_symbol).subquery('latest_dates')

    latest_times = db.session.query(
        latest_timestamps.c.stock_symbol,
        latest_timestamps.c.max_date,
        func.max(LiveIndicatorValue.time).label('max_time')
    ).join(
        LiveIndicatorValue,
        db.and_(
            LiveIndicatorValue.stock_symbol == latest_timestamps.c.stock_symbol,
            LiveIndicatorValue.date == latest_timestamps.c.max_date
        )
    ).group_by(
        latest_timestamps.c.stock_symbol,
        latest_timestamps.c.max_date
    ).subquery('latest_times')

    # Modified query to properly join with LiveStockPrice
    latest_records = db.session.query(
        LiveIndicatorValue,
        LiveStockPrice.price.label('ltp')
    ).join(
        latest_times,
        db.and_(
            LiveIndicatorValue.stock_symbol == latest_times.c.stock_symbol,
            LiveIndicatorValue.date == latest_times.c.max_date,
            LiveIndicatorValue.time == latest_times.c.max_time
        )
    ).join(
        LiveStockPrice,
        db.and_(
            LiveStockPrice.stock_symbol == LiveIndicatorValue.stock_symbol,
            LiveStockPrice.date == LiveIndicatorValue.date,
            LiveStockPrice.time == LiveIndicatorValue.time
        )
    ).order_by(LiveStockPrice.time.desc()).all()

    result = {}
    for record, ltp in latest_records:  # Now we get both the record and the price
        key = f"{record.stock_symbol}_{record.date}_{record.time}"
        if key not in result:
            result[key] = {
                "stock_symbol": record.stock_symbol,
                "date": record.date.isoformat(),
                "time": record.time.strftime("%H:%M:%S"),
                "ltp": ltp  # Using the joined price value
            }

        # Rest of your indicator logic remains the same
        if record.indicator_name == 'RSI':
            result[key]["RSI"] = "Buy" if record.value < 30 else "Sell" if record.value > 70 else "Hold"
        elif record.indicator_name == 'ADX':
            result[key]["ADX"] = "Strong Trend" if record.value > 25 else "Weak Trend"
        elif record.indicator_name == 'Momentum':
            result[key]["Momentum"] = "Buy" if record.value > 0 else "Sell"
        elif record.indicator_name == 'SMA':
            result[key]["SMA"] = "Buy" if record.value > 50 else "Sell"
        elif record.indicator_name == 'OBV':
            result[key]["OBV"] = "Buy" if record.value > 0 else "Sell"

    return jsonify(list(result.values()))


# Live data route (?debug=true)
@app.route('/api/live-indicators')
def get_live_indicators():
    # Get the latest indicator values for each stock
    # First, get distinct stock symbols with their latest date and time
    latest_timestamps = db.session.query(
        LiveIndicatorValue.stock_symbol,
        func.max(LiveIndicatorValue.date).label('max_date')
    ).group_by(LiveIndicatorValue.stock_symbol).subquery('latest_dates')
    
    # Then, for each stock and its latest date, get the latest time
    latest_times = db.session.query(
        latest_timestamps.c.stock_symbol,
        latest_timestamps.c.max_date,
        func.max(LiveIndicatorValue.time).label('max_time')
    ).join(
        LiveIndicatorValue,
        db.and_(
            LiveIndicatorValue.stock_symbol == latest_timestamps.c.stock_symbol,
            LiveIndicatorValue.date == latest_timestamps.c.max_date
        )
    ).group_by(
        latest_timestamps.c.stock_symbol,
        latest_timestamps.c.max_date
    ).subquery('latest_times')
    
    # Finally, get all indicator values for each stock at its latest timestamp
    latest_records = db.session.query(LiveIndicatorValue).join(
        latest_times,
        db.and_(
            LiveIndicatorValue.stock_symbol == latest_times.c.stock_symbol,
            LiveIndicatorValue.date == latest_times.c.max_date,
            LiveIndicatorValue.time == latest_times.c.max_time
        )
    ).all()
    
    # Organize the data by stock symbol, date, and time
    result = {}
    for record in latest_records:
        key = f"{record.stock_symbol}_{record.date}_{record.time}"
        if key not in result:
            result[key] = {
                "stock_symbol": record.stock_symbol,
                "date": record.date.isoformat(),
                "time": record.time.strftime("%H:%M:%S")
            }
        
        # Add each indicator to the result with NaN handling
        if record.value is not None and not (isinstance(record.value, float) and math.isnan(record.value)):
            result[key][record.indicator_name] = record.value
        else:
            result[key][record.indicator_name] = None
    
    # Convert to list and return
    return jsonify(list(result.values()))


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


# Core page signal route buy/sell 
@app.route('/api/signals', methods=['GET'])
def get_companies():
    companies = Stock.query.order_by(Stock.symbol).all()
    company_data = []
    
    for company in companies:
        latest_indicator = (
            IndicatorValues.query
            .filter_by(stock_symbol=company.symbol)
            .order_by(IndicatorValues.date.desc())  # Get the latest entry
            .limit(2)
            .all()
        )

        # Fetch the latest closing price (LTP) for the company
        latest_stock_price = (
            StockPrice.query
            .filter_by(stock_symbol=company.symbol)
            .order_by(StockPrice.date.desc())  # Get the latest entry
            .limit(2)
            .all()
        )

        if len(latest_indicator) >= 2 and len(latest_stock_price) >= 2:
            current_obv = latest_indicator[0].obv
            previous_obv = latest_indicator[1].obv
            current_price = latest_stock_price[0].close_price
            previous_price = latest_stock_price[1].close_price

            # Determine OBV and Price Trends
            obv_rising = current_obv > previous_obv
            price_rising = current_price > previous_price

            # OBV Buy/Sell Signal (Trend Confirmation)
            obv_signal = "Buy" if (obv_rising and price_rising) else (
                        "Sell" if (not obv_rising and not price_rising) else "Hold"
            )
        
        # Extract the latest values properly
        latest = latest_indicator[0]
        signals = {
            "RSI": "Buy" if latest.rsi < 30 else "Sell" if latest.rsi > 70 else "Hold",
            "ADX": "Strong Trend" if latest.adx > 25 else "Weak Trend",
            "Momentum": "Buy" if latest.momentum > 0 else "Sell",
            "SMA": "Buy" if latest.sma < current_price else "Sell",
            "OBV": obv_signal
        }

        buy_count = sum(1 for signal in signals.values() if signal == "Buy")
        sell_count = sum(1 for signal in signals.values() if signal == "Sell")
        hold_count = sum(1 for signal in signals.values() if signal == "Hold")

        signals_count = [buy_count, sell_count, hold_count]

        company_data.append({
            "symbol": company.symbol,
            "date": latest.date.strftime("%Y-%m-%d"),
            "close_price": current_price,
            "signals": signals,
            "signals_count": signals_count
        })
    
    return jsonify(company_data)


# Indicator values from database route (core ?debug=true)
@app.route('/api/indicators', methods=['GET'])
def get_latest_indicators():
    latest_dates = db.session.query(
        IndicatorValues.stock_symbol,
        func.max(IndicatorValues.date).label("latest_date")
    ).group_by(IndicatorValues.stock_symbol).subquery()

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

    indicators_data = [
        {
            "symbol": ind.stock_symbol,
            "date": ind.date.strftime('%Y-%m-%d'),
            "signals": {
                "RSI": round(ind.rsi, 2),  # Round to 2 significant digits
                "SMA": round(ind.sma, 2),
                "OBV": round(ind.obv, 2),
                "ADX": round(ind.adx, 2),
                "Momentum": round(ind.momentum, 2)
            }
        }
        for ind in latest_indicators
    ]


    return jsonify(indicators_data)


# Company page HTML route
@app.route('/company/<symbol>')
def company_page(symbol):
    return render_template('company.html', symbol=symbol)


# API route to fetch company data
@app.route('/api/company/<symbol>/data')
def company_data_api(symbol):
    three_months = datetime.now() - timedelta(days=90)

    # Keep in ascending order for charting
    stock_prices = StockPrice.query.filter(
        StockPrice.stock_symbol == symbol,
        StockPrice.date >= three_months
    ).order_by(StockPrice.date.asc()).all()

    indicator_values = IndicatorValues.query.filter(
        IndicatorValues.stock_symbol == symbol,
        IndicatorValues.date >= three_months
    ).order_by(IndicatorValues.date.asc()).all()

    company = Stock.query.filter(Stock.symbol == symbol).first()

    # Prepare stock price data
    stock_data = [{
        'date': price.date.strftime('%Y-%m-%d'),
        'open': price.open_price,
        'close': price.close_price,
        'high': price.high,
        'low': price.low,
        'volume': price.volume,
        'symbol': price.stock_symbol
    } for price in stock_prices]

    # Prepare indicator data
    indicator_data = [{
        'date': value.date.strftime('%Y-%m-%d'),
        'rsi': value.rsi,
        'sma': value.sma,
        'obv': value.obv,
        'adx': value.adx,
        'momentum': value.momentum
    } for value in indicator_values]

    # Signal logic (get last two items from ASC list)
    signals = {}
    if len(indicator_values) >= 2 and len(stock_prices) >= 2:
        latest_indicator = indicator_values[-1]
        prev_indicator = indicator_values[-2]
        latest_price = stock_prices[-1]
        prev_price = stock_prices[-2]

        current_obv = latest_indicator.obv
        previous_obv = prev_indicator.obv
        current_price = latest_price.close_price
        previous_price = prev_price.close_price

        obv_rising = current_obv > previous_obv
        price_rising = current_price > previous_price
        obv_signal = "Buy" if (obv_rising and price_rising) else (
            "Sell" if (not obv_rising and not price_rising) else "Hold"
        )

        signals = {
            "RSI": "Buy" if latest_indicator.rsi < 30 else "Sell" if latest_indicator.rsi > 70 else "Hold",
            "ADX": "Strong Trend" if latest_indicator.adx > 25 else "Weak Trend",
            "Momentum": "Buy" if latest_indicator.momentum > 0 else "Sell",
            "SMA": "Buy" if latest_indicator.sma < current_price else "Sell",
            "OBV": obv_signal
        }

    company_data = {
        'company_name': company.name if company else 'Unknown',
        'symbol': symbol,
        'sector': company.sector if company else 'Unknown'
    }

    return jsonify({
        'stock_data': stock_data,
        'indicator_data': indicator_data,
        'company_data': company_data,
        'latest_signals': signals
    })



# Indicator data route for pop up graph
@app.route('/indicator_data/<string:symbol>/<string:indicator>', methods=['GET'])
def get_indicator_data(symbol, indicator):
    # Validate indicator name to avoid SQL injection or invalid columns
    allowed_indicators = ['rsi', 'sma', 'obv', 'adx', 'momentum']
    if indicator not in allowed_indicators:
        return jsonify({'error': 'Invalid indicator'}), 400

    try:
        today = datetime.today().date()
        start_date = today - timedelta(days=25)  # buffer to ensure at least 14 available days

        # Query only the needed indicator and date
        results = db.session.query(
            IndicatorValues.date,
            getattr(IndicatorValues, indicator)
        ).filter(
            IndicatorValues.stock_symbol == symbol,
            IndicatorValues.date >= start_date
        ).order_by(IndicatorValues.date).limit(14).all()

        data = [{
            'date': r.date.strftime('%Y-%m-%d'),
            'value': r[1]
        } for r in results if r[1] is not None]

        latest_value = data[-1]['value'] if data else None

        return jsonify({
            'symbol': symbol,
            'indicator': indicator,
            'data': data,
            'latest_value': latest_value
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
