from flask import flash, redirect, render_template, request, session, url_for
from app.models import User, db
from . import router
import re

@router.route('/')
def home():
    return render_template('home.html')

def is_valid_email(email):
    """
    Validate the format of an email address using regex.
    
    Args:
        email (str): The email address to validate.
    
    Returns:
        bool: True if the email is valid, False otherwise.
    """
    # Regex pattern for a valid email address
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email) is not None

def is_strong_password(password):
    """
    Validate the strength of a password using regex.
    
    Args:
        password (str): The password to validate.
    
    Returns:
        bool: True if the password is strong, False otherwise.
    """
    # Regex pattern for a strong password
    regex = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(regex, password) is not None


@router.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            name = request.form['name']
            surname = request.form['surname']
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            role = request.form.get('role', 'student')

            # Input validation
            if not name or not surname or not username or not email or not password or not confirm_password:
                flash('All fields are required.', 'error')
                return redirect(url_for('main.signup'))

            if len(username) < 4:
                flash('Username must be at least 4 characters long.', 'error')
                return redirect(url_for('main.signup'))

            if not is_valid_email(email):
                flash('Invalid email address. Please provide a valid email.', 'error')
                return redirect(url_for('main.signup'))

            if not is_strong_password(password):
                flash('Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one digit, and one special character.', 'error')
                return redirect(url_for('main.signup'))

            if password != confirm_password:
                flash('Passwords do not match. Please try again.', 'error')
                return redirect(url_for('main.signup'))

            # Check if username or email already exists
            existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
            if existing_user:
                if existing_user.username == username:
                    flash('Username already exists. Please choose a different one.', 'error')
                else:
                    flash('Email already exists. Please use a different email.', 'error')
                return redirect(url_for('main.signup'))

            # Create new user
            new_user = User(
                name=name,
                surname=surname,
                username=username,
                email=email,
                role=role
            )
            new_user.set_password(password)

            # Save to database
            db.session.add(new_user)
            db.session.commit()

            # Set session variables
            session['user_id'] = new_user.user_id
            session['role'] = new_user.role
            session['username'] = new_user.username

            # Redirect based on role
            if new_user.role == 'student':
                flash('Sign-up successful! You are now logged in.', 'success')
                return redirect(url_for('main.student_dashboard'))
            elif new_user.role == 'tutor':
                flash('Sign-up successful! You are now logged in.', 'success')
                return redirect(url_for('main.tutor_dashboard'))

        except Exception as e:
            db.session.rollback()
            flash('Something went wrong. Please try again later.', 'error')
            print(f"Error during signup: {str(e)}")
            return redirect(url_for('main.signup'))

    return render_template('signup.html')

@router.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username_or_email = request.form['username'] 
            password = request.form['password']

            # Input validation
            if not username_or_email or not password:
                flash('Username/Email and password are required.', 'error')
                return redirect(url_for('main.login'))

            # Check if user exists by username or email
            user = User.query.filter(
                (User.username == username_or_email) | (User.email == username_or_email)
            ).first()

            # Verify password
            if not user or not user.check_password(password):
                flash('Invalid username/email or password.', 'error')
                return redirect(url_for('main.login'))

            # Set session variables
            session['user_id'] = user.user_id
            session['role'] = user.role
            session['username'] = user.username

            # Redirect based on role
            if user.role == 'student':
                return redirect(url_for('main.student_dashboard'))
            elif user.role == 'tutor':
                return redirect(url_for('main.tutor_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('main.admin_dashboard'))
            else:
                flash('Invalid role assigned to user.', 'error')
                return redirect(url_for('main.login'))

        except Exception as e:
            flash('Something went wrong. Please try again later.', 'error')
            print(f"Error during login: {str(e)}")
            return redirect(url_for('main.login'))

    return render_template('login.html')

@router.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.login'))