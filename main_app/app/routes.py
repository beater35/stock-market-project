from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from app import app, db, bcrypt  
from sqlalchemy.exc import IntegrityError
from app.models import User  


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



# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))



if __name__ == "__main__":
    app.run(debug=True)
