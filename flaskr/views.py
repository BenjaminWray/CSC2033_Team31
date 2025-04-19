from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_user, current_user, login_required, logout_user
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
from forms import SignUpForm, LoginForm
from models.database import db, create_user, User, login_manager, Quiz, get_user_by_id

auth_bp = Blueprint('auth', __name__)

# Index page
@auth_bp.route('/')
def index():
    return render_template('index.html')

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


# Admin dashboard with search + pagination
@auth_bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    search_query = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 5  # users per page

    query = User.query
    if search_query:
        query = query.filter(
            or_(
                User.username.ilike(f"%{search_query}%"),
                User.email.ilike(f"%{search_query}%")
            )
        )

    users = query.order_by(User.id).paginate(page=page, per_page=per_page)
    return render_template("admin_dashboard.html", users=users)

@auth_bp.route('/admin/update_role/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def update_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')

    if new_role not in ['user', 'admin']:
        flash("Invalid role.", "danger")
    else:
        user.role = new_role
        db.session.commit()
        flash(f"User {user.username} role changed to {new_role}.", "success")

    return redirect(url_for('auth.admin_dashboard'))


@auth_bp.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.username} deleted.", "success")
    return redirect(url_for('auth.admin_dashboard'))

# Home route
@auth_bp.route('/home')
def home():
    return render_template('home.html')


# User account route
@auth_bp.route('/account')
@login_required
def account():
    return render_template('account.html', user=current_user )


@auth_bp.route('/quiz_history')
@login_required
def quiz_history():
    return render_template("quiz_history.html")


@auth_bp.route('/leaderboard')
@login_required
def leaderboard():
    return render_template("leaderboard.html")

@auth_bp.route('/quizzes', methods=['GET'])
def quizzes():
    # Get all quizzes and their respective user information
    quiz_dict = {}
    for quiz in db.session.query(Quiz).all():
        quiz_dict[quiz] = get_user_by_id(quiz.user_id)
    return render_template("quizzes.html", quizzes=quiz_dict)


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
                return redirect(url_for('auth.home'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('auth.index'))
