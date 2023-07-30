from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length

class SignUpForm(FlaskForm):
    """Form for signing up a new user."""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(),  Length(min=6)])
    
class LoginForm(FlaskForm):
    """Form for logging in a user."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3)])
    password = PasswordField('Password', validators=[ Length(min=6)])

class EditUserForm(FlaskForm):
    ''' Form for editing a user's profile'''
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    
    
