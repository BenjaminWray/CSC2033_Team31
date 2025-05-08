from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number')
    location = StringField('Location (e.g., Newcastle, UK)')
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class QuizSearchForm(FlaskForm):
    search_query = StringField('Search:')
    search_by = SelectField('Search by:', choices=[('title', 'Title'), ('user', 'User')])
    sort_by = SelectField('Sort by:', choices=[('date', 'Date'), ('title', 'Title'), ('user', 'User'), ('question_count', 'Question Count')])
    sort_order = SelectField('Order:', choices=[('desc', 'Descending'), ('asc', 'Ascending')])
    submit = SubmitField('Search')

