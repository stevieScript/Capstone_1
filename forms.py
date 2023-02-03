from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, EmailField
from wtforms.validators import DataRequired, Email, Length


class SignUpForm(FlaskForm):
    """Form for signing up a new user."""

    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=25)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    user_img = StringField('Image URL (Optional) ')


class LoginForm(FlaskForm):
    """Form for logging in a user."""

    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=25)])




