import math
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, session
from flask_login import login_user, current_user, login_required, logout_user
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import Leaderboard
from sqlalchemy.orm import joinedload
from forms import SignUpForm, LoginForm, QuizSearchForm, CreateQuizForm
from models.database import db, create_user, User, login_manager, Quiz, get_user_by_id, Question, create_quiz, \
    create_question, create_answer
#, create_question, create_answer
from mail import reg_email

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


# Helper function for account rendering
def render_account_page(message=None, error=None):
    return render_template('account.html', user=current_user, message=message, error=error)


# User account route
@auth_bp.route('/account')
@login_required
def account():
    if current_user.username.lower() == 'guest':
        flash("🚫 Guests are not allowed to access the account page.", "danger")
        return redirect(url_for('auth.home'))
    return render_template('account.html', user=current_user)

@auth_bp.route('/quiz_history')
@login_required
def quiz_history():
    return render_template("quiz_history.html")


# Username change handler
@auth_bp.route('/change_username', methods=['POST'])
@login_required
def change_username():
    new_username = request.form.get('new_username', '').strip()

    if not new_username:
        return render_account_page(error="Username cannot be empty.")

    if new_username == current_user.username:
        return render_account_page(error="New username is the same as current username.")

    if User.query.filter_by(username=new_username).first():
        return render_account_page(error="Username already exists.")

    current_user.username = new_username
    db.session.commit()
    return render_account_page(message="Username updated successfully!")

@auth_bp.route('/leaderboard')
@login_required
def leaderboard():
    top_users = Leaderboard.query.options(joinedload(Leaderboard.user)) \
        .order_by(Leaderboard.total_score.desc()) \
            .limit(20).all()

    return render_template("leaderboard.html", top_users=top_users)


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

# Quiz creation route
@auth_bp.route('/quizzes/create_new_quiz', methods=['GET', 'POST'])
@login_required
def create_new_quiz():
    # Load form from session or create new form if no form exists
    if 'create_quiz_form' not in session: session['create_quiz_form'] = CreateQuizForm().data
    form = CreateQuizForm(data=session.get('create_quiz_form'))

    if form.is_submitted() and form.change_length.data:
        # Reload page with new quiz length
        session['create_quiz_form'] = form.data
        return redirect(url_for('auth.create_new_quiz'))
    elif form.validate_on_submit():
        # Create new quiz
        quiz = create_quiz(form.title.data, current_user.id)
        for qna in form.questions:
            question = create_question(quiz_id=quiz.id, content=qna.form.question.data, difficulty=qna.form.difficulty.data, topic=qna.form.topic.data)
            create_answer(question.id, qna.form.answer.data)
        session.pop('create_quiz_form')
        return redirect(url_for('auth.quizzes'))

    # Update length of questions field list
    current_length = len(form.questions)
    if form.length.data < current_length: form.questions = form.questions[:form.length.data]
    elif form.length.data > current_length:
        for _ in range(form.length.data - current_length):
            form.questions.append_entry()

    return render_template("create_new_quiz.html", form=form)

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

        # send a registration email to the users email address
        reg_email(form.email.data)

        flash('Account created successfully. You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    elif form.is_submitted():
        print("DEBUG: Form submitted but not validated")
        print(form.errors)  # Print validation errors

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

@auth_bp.route('/guest_login')
def guest_login():
    guest_user = User.query.filter_by(username='guest').first()

    if not guest_user:
        guest_user = User(
            username='guest',
            email='guest@example.com',
            password_hash=generate_password_hash('guest123'),
            role='user'
        )
        db.session.add(guest_user)
        db.session.commit()
        guest_user.generate_log()

    login_user(guest_user)
    flash("You are now logged in as a guest.", "info")
    return redirect(url_for('auth.home'))


@auth_bp.route('/quizzes_guest')
def quizzes_guest():
    quizzes = Quiz.query.all()
    return render_template('quizzes_guest.html', quizzes=quizzes, guest_mode=True) # Use guest view quiz page

@auth_bp.route('/guest_quiz_attempt/<int:quiz_id>', methods=['GET', 'POST'])
def guest_quiz_attempt(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions

    if request.method == 'POST':
        submitted_answers = request.form.to_dict() # allowing for guest scoring
        results = []
        score = 0

        for question in questions: # Scoring of guest quiz
            selected = submitted_answers.get(str(question.id))
            correct = next((a for a in question.answers if a.is_correct), None)
            is_correct = str(correct.id) == selected
            if is_correct:
                score += 1

            results.append({ # Creating results for view after quiz is complete
                'question': question.content,
                'selected': selected,
                'correct': correct.content,
                'is_correct': is_correct
            })

        return render_template('guest_quiz_results.html', results=results, score=score, total=len(questions))

    return render_template('guest_quiz_attempt.html', quiz=quiz, questions=questions)
