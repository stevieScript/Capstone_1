from flask import Flask, render_template, flash, redirect, request, session, g
from flask_debugtoolbar import DebugToolbarExtension
from routes.user import user_bp
from routes.playlists import playlist_bp
from routes.songs import songs_bp
from routes.albums import albums_bp

from helper_functions import (
    get_token,
    generic_search,
)

from models import  connect_db, User

import os

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql:///maestro"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "maestro2468")
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

debug = DebugToolbarExtension(app)

connect_db(app)

# User routes
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

@app.route("/")
def homepage():
    """Show homepage."""
    if g.user:
        return redirect(f"/user")
    else:
        return render_template("base.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    """Search for songs on Spotify."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = User.query.get_or_404(g.user.id)

    if request.method == "GET":
        search_type = request.args.get("search_type")
        search_term = request.args.get("search_term")
        if search_term and search_type:
            token = get_token()
            result = generic_search(search_type, search_term, token)
            return render_template(
                "/music/search_results.html",
                result=result,
                user=user,
                search_term=search_term,
            )
        else:
            return render_template("/music/search.html", user=user)
    else:
        return render_template("/music/search.html", user=user)


app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(songs_bp, url_prefix='/songs')
app.register_blueprint(albums_bp, url_prefix='/albums')
app.register_blueprint(playlist_bp, url_prefix='/playlists')


@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""
    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers["Cache-Control"] = "public, max-age=0"
    return req
