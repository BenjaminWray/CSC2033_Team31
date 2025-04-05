from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import SignUpForm, LoginForm
from models.database import db, create_user, User, login_manager

auth_bp = Blueprint('auth', __name__)


# Admin access restriction decorator
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return login_manager.unauthorized()

        if current_user.role.strip() != 'admin':
            abort(403)

        return f(*args, **kwargs)
    return wrapper


# Admin dashboard route
@auth_bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)


# User registration route
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()

    if form.validate_on_submit():

        # Check for existing username/email
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken.', 'danger')
            return redirect(url_for('auth.signup'))

        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.signup'))

        # Hash the password
        hashed_password = generate_password_hash(form.password.data)

        # Create new user
        new_user = create_user(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            phone_number=form.phone_number.data,
            location=form.location.data
        )

        # Create log entry
        new_user.generate_log()
        db.session.commit()

        flash('Account created successfully. You can now log in.', 'success')
        return render_template('signup.html', form=form)

    elif form.is_submitted():
        return render_template('signup.html', form=form)

    return render_template('signup.html', form=form)


# User login route
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            db.session.commit()
            flash('Logged in successfully.', 'success')

            if user.role == 'admin':
                return redirect(url_for('auth.admin_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))