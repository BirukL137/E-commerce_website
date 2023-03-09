# Import necessary modules
from wtforms import BooleanField, StringField, PasswordField, validators , ValidationError
from flask_wtf import FlaskForm, Form
from .models import User

# Define RegistrationForm class that inherits from FlaskForm
class RegistrationForm(FlaskForm):
    name = StringField('Name', [validators.Length(min=4, max=25)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

    # Define a custom validation function for the username field
    def validate_username(self, field):
        # Check if the entered username already exists in the User model
        if User.query.filter_by(username=field.data).first():
            # If the username exists, raise a validation error
            raise ValidationError('Username already in use.')

    # Define a custom validation function for the email field
    def validate_email(self, field):
        # Check if the entered email already exists in the User model
        if User.query.filter_by(email=field.data).first():
            # If the email exists, raise a validation error
            raise ValidationError('Email already registered.')
     


# Define the LoginForm class that inherits from FlaskForm
class LoginForm(FlaskForm):
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [validators.DataRequired()])
