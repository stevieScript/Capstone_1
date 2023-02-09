from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from helper_functions import get_token, search_artist, get_songs, generic_search, get_audio_analysis, get_albums, get_album, get_album_tracks, get_album_art

from forms import SignUpForm, LoginForm, SpotifySearchForm 
from models import db, connect_db, User, Song, Artist, ArtistSong, Playlist, PlaylistSong

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///maestro'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = 'maestro'
toolbar = DebugToolbarExtension(app)

connect_db(app)


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/')
def homepage():
    """Show homepage."""
    if g.user:
        return render_template('home.html')
    else:
        return render_template('base.html')

@app.route('/register', methods=["GET", "POST"])
def signup():
    """Handle user signup."""
    form = SignUpForm()

    if form.validate_on_submit():
        try:
            user = User.register(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                # user_img=form.user_img.data
            )
            db.session.commit()
        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('register.html', form=form)
        
        do_login(user)
        flash(f"Welcome, maestro {user.username}!", 'success')
        return redirect(f'/users/{user.id}')

    else:
        return render_template('register.html', form=form)
    

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)
        if user:
            do_login(user)
            return redirect(f'/user/{user.id}')

        flash("Invalid credentials.", 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash("Logged out", 'success')
    return redirect('/')


@app.route('/user/<int:user_id>')
def user_profile(user_id):
    """Show user profile."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('user.html', user=user)


# @app.route('/users/<int:user_id>/delete', methods=["POST"])
# def delete_user(user_id):
#     """Delete user."""

#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     user = User.query.get_or_404(user_id)
#     db.session.delete(user)
#     db.session.commit()
#     do_logout()
#     flash("User deleted", 'success')
#     return redirect('/')

# @app.route('/users/<int:user_id>/edit', methods=["GET", "POST"])
# def edit_user(user_id):
#     """Edit user profile."""

#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     user = User.query.get_or_404(user_id)
#     form = SignUpForm(obj=user)

#     if form.validate_on_submit():
#         user.username = form.username.data
#         user.email = form.email.data
#         user.user_img = form.user_img.data

#         db.session.commit()
#         flash("User updated", 'success')
#         return redirect(f"/users/{user.id}")

#     else:
#         return render_template('edit_user.html', form=form, user=user)
    


# @app.route('/users/<int:user_id>/playlists')
# def show_playlists(user_id):
#     """Show user playlists."""

#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     user = User.query.get_or_404(user_id)
#     return render_template('playlists.html', user=user)

@app.route('/user/<int:user_id>/search', methods=["GET", "POST"])
def search(user_id):
    """Search for songs on Spotify."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = SpotifySearchForm()

    user = User.query.get_or_404(user_id)

    if form.validate_on_submit():
        token = get_token()
        result = generic_search(form.search_type.data, form.search_term.data, token)
        return render_template('search_results.html', result=result, user=user)
    else:
        return render_template('search.html', form=form)
    
@app.route('/audio_analysis/<track_id>')
def audio_analysis(track_id):
    """Show audio analysis of song."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    token = get_token()
    result = get_audio_analysis(track_id, token)
    
    return render_template('audio_analysis.html', result=result)
    


# @app.after_request
# def add_header(req):
#     """Add non-caching headers on every request."""

#     req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     req.headers["Pragma"] = "no-cache"
#     req.headers["Expires"] = "0"
#     req.headers['Cache-Control'] = 'public, max-age=0'
#     return req