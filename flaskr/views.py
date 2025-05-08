import math
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_user, current_user, login_required, logout_user
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
from forms import SignUpForm, LoginForm, QuizSearchForm
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
    top_users = User.query.order_by(User.results.desc()).limit(20).all()


    return render_template("leaderboard.html" , top_users =top_users)

@auth_bp.route('/quizzes', methods=['GET', 'POST'])
def quizzes():
    form = QuizSearchForm()

    # Pagination setup
    if form.validate_on_submit(): page_number = 1
    else: page_number = request.args.get('page', 1, type=int)
    max_items = request.args.get('items', 15, type=int)

    # Prevent negative page numbers
    if page_number < 1: return redirect(url_for('auth.quizzes', form=form, page=1, items=max_items))

    # Query to fetch quizzes from the database
    quiz_query = db.session.query(Quiz)

    # Filter query by search term
    if form.validate_on_submit():
        search_term = form.search_query.data.strip()
        if search_term:
            if form.search_by.data == 'title':
                quiz_query = quiz_query.filter(Quiz.title.ilike(f'%{search_term}%'))
            elif form.search_by.data == 'user':
                quiz_query = quiz_query.filter(Quiz.user_id == User.id, User.username.ilike(f'%{search_term}%'))

    # Check if the query returns no results
    if quiz_query.count() == 0: return render_template("quizzes.html", form=form, quizzes={}, pn=1, pmax=1, imax=max_items)

    # Calculate total number of pages and prevent out-of-range page numbers
    max_pages = math.ceil(quiz_query.count() / max_items)
    if page_number > max_pages: return redirect(url_for('auth.quizzes', page=max_pages, items=max_items))

    # Get quizzes and user information for the current page
    quiz_list = quiz_query.all()[(page_number - 1) * max_items:page_number * max_items]
    users = {}
    for quiz in quiz_list: users[quiz] = get_user_by_id(quiz.user_id)

    # Sort the quizzes based on form data
    if form.validate_on_submit():
        match form.sort_by.data:
            case 'date': sort_func=lambda x: x.created_at
            case 'title': sort_func=lambda x: x.title
            case 'user': sort_func=lambda x: users[x].username
            case 'question_count': sort_func=lambda x: x.question_count()
            case _: sort_func=lambda x: x.id
        quiz_list.sort(key=sort_func, reverse=form.sort_order.data == "desc")
    else:
        # Default sorting by date in descending order
        quiz_list.sort(key=lambda x: x.created_at, reverse=True)

    return render_template("quizzes.html", form=form, quizzes=quiz_list, users=users, pn=page_number, pmax=max_pages, imax=max_items)
@auth_bp.route('/submitquiz',methods=['POST'])
@login_required
def submit_quiz():
    quiz_id = request.form.get('quiz_id')
    user_id = current_user.id
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        flash("Quiz not found.", "danger")
        return redirect(url_for('auth.home'))

    total_score = 0
    time_taken = request.form.get('time_taken')  # Time taken for the quiz in seconds
    answers = request.form.getlist('answers')  # List of selected answers for each question

    # Calculate the score based on the answers
    for answer_id in answers:
        answer = Answer.query.get(answer_id)
        if answer and answer.is_correct:
            total_score += 1  # Award 1 point per correct answer

    # Create a QuizResult entry
    quiz_result = QuizResult(
        quiz_id=quiz_id,
        user_id=user_id,
        score=total_score,
        time_taken=time_taken
    )
    db.session.add(quiz_result)
    db.session.commit()

    # Update the User's points based on the quiz score
    user = User.query.get(user_id)
    user.results += total_score  # Add the score to the user's total points
    db.session.commit()

    # Optionally, update leaderboard or other relevant stats
    leaderboard = Leaderboard.query.filter_by(user_id=user.id).first()
    if leaderboard:
        leaderboard.total_score += total_score
        leaderboard.quizzes_completed += 1
        leaderboard.average_time = (
                (leaderboard.average_time * (leaderboard.quizzes_completed - 1) + int(time_taken))
                / leaderboard.quizzes_completed
        )

        db.session.commit()

    flash(f"Your score is {total_score}!", "success")
    return redirect(url_for('auth.quiz_history'))
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

@auth_bp.route('/flashcards', methods=['GET'])
@login_required
def flashcards():
    """Display flashcards for a specific topic or all topics."""
    topic = request.args.get('topic', None)
    if topic:
        questions = Question.query.filter_by(topic=topic).all()
    else:
        questions = Question.query.all()
    return render_template('flashcards.html', questions=questions)


@auth_bp.route('/flashcards/new', methods=['GET', 'POST'])
@login_required
def new_flashcard():
    """Create a new flashcard."""
    form = FlashcardForm()
    if form.validate_on_submit():
        existing_question = Question.query.filter_by(content=form.question.data).first()
        if existing_question:
            flash('A flashcard with this question already exists.', 'danger')
            return redirect(url_for('auth.new_flashcard'))
        try:
            question = create_question(
                content=form.question.data,
                difficulty=form.difficulty.data,
                topic=form.topic.data
            )
            create_answer(
                question_id=question.id,
                content=form.answer.data
            )
            flash('Flashcard created successfully!', 'success')
            return redirect(url_for('auth.flashcards'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", 'danger')
            return redirect(url_for('auth.new_flashcard'))
    return render_template('new_flashcard.html', form=form)