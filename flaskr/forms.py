from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, Optional, ValidationError


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

class QuizSearchForm(FlaskForm):
    search_query = StringField('Search:')
    search_by = SelectField('Search by:', choices=[('title', 'Title'), ('user', 'User')])
    sort_by = SelectField('Sort by:', choices=[('date', 'Date'), ('title', 'Title'), ('user', 'User'), ('question_count', 'Question Count')])
    sort_order = SelectField('Order:', choices=[('desc', 'Descending'), ('asc', 'Ascending')])
    submit = SubmitField('Search')

