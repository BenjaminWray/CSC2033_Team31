from flask_wtf import FlaskForm , RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, SelectField, FieldList, FormField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, Optional, ValidationError, NumberRange
from models.database import get_quiz_by_id


def validate_common_email_domain(form, field):
    allowed_domains = [
        'gmail.com', 'outlook.com', 'hotmail.com', 'icloud.com',
        'yahoo.com', 'live.com', 'qq.com', 'mail.com', 'aol.com'
    ]
    domain = field.data.split('@')[-1].lower()
    if domain not in allowed_domains:
        raise ValidationError("Please use a common email provider (e.g., Gmail, Outlook).")


class SignUpForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(min=4, max=50),
            Regexp(r'^[A-Za-z0-9_]+$', message="Username can only contain letters, numbers, and underscores.")
        ]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(message="Please enter a valid email address."),
            validate_common_email_domain
        ]
    )

    phone_number = StringField(
        'Phone Number',
        validators=[
            Optional(),
            Regexp(
                r'^(07\d{9}|\+447\d{9})$',
                message="Enter a valid UK phone number (07xxxxxxxxx or +447xxxxxxxxx)"
            )
        ]
    )

    location = SelectField(
        'Location (optional)',
        choices=[
            ('', 'Select your location'),
            ('newcastle', 'Newcastle, UK'),
            ('london', 'London, UK'),
            ('manchester', 'Manchester, UK'),
            ('edinburgh', 'Edinburgh, UK'),
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters long."),
            Regexp(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$',
                message="Password must include at least one lowercase letter, one uppercase letter, and one number."
            )
        ]
    )

    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match')
        ]
    )

    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    recaptcha = RecaptchaField()

class QuizSearchForm(FlaskForm):
    search_query = StringField('Search:')
    search_by = SelectField('Search by:', choices=[('title', 'Title'), ('user', 'User')])
    sort_by = SelectField('Sort by:', choices=[('date', 'Date'), ('title', 'Title'), ('user', 'User'), ('question_count', 'Question Count')])
    sort_order = SelectField('Order:', choices=[('desc', 'Descending'), ('asc', 'Ascending')])
    submit = SubmitField('Search')

class QuestionAnswerForm(FlaskForm):
    question = StringField('Question', validators=[Length(min=1)])
    answer = StringField('Answer', validators=[Length(min=1)])
    difficulty = SelectField('Difficulty', choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')])
    topic = StringField("Topic", validators=[Length(min=1)])

    def load_question(self, question):
        self.question.data = question.content
        self.answer.data = question.answers[0].content
        self.difficulty.data = question.difficulty
        self.topic.data = question.topic
        return self

class CreateQuizForm(FlaskForm):
    title = StringField('Title', validators=[Length(min=1)])
    length = IntegerField('Number of questions', default=1, validators=[DataRequired(), NumberRange(min=1, max=9999)])
    change_length = SubmitField('Change quiz length')
    questions = FieldList(FormField(QuestionAnswerForm))
    submit = SubmitField('Save quiz')

    def load_quiz(self, quiz_id):
        quiz = get_quiz_by_id(quiz_id)
        self.title.data = quiz.title
        for question in quiz.questions: self.questions.append_entry(data=QuestionAnswerForm().load_question(question).data)
        return self