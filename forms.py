from flask_wtf import FlaskForm
from wtforms import StringField,RadioField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Length


class SignUpForm(FlaskForm):
    """Form for signing up a new user."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    # user_img = StringField('Image URL (Optional) ')


class LoginForm(FlaskForm):
    """Form for logging in a user."""

    username = StringField('Username', validators=[DataRequired(), Length(min=3)])
    password = PasswordField('Password', validators=[ Length(min=6)])

class SpotifySearchForm(FlaskForm):
    ''' Form for searching Spotify'''

    search_term = StringField('Search')

    search_type = SelectField('Search Type', choices=[('track', 'Track'), ('artist', 'Artist'), ('album', 'Album')])
    



