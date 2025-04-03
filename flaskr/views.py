from flask import Blueprint, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from forms import SignUpForm
from models.database import db, create_user, User

auth_bp = Blueprint('auth', __name__)

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

        flash('Account created successfully. You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('signup.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')