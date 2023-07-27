from flask import Flask, render_template, flash, redirect, request, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from helper_functions import (
    get_token,
    generic_search,
    get_audio_analysis,
    get_albums,
    get_album_tracks,
    get_pop_recommendations,
)

from forms import (
    SignUpForm,
    LoginForm,
    SpotifySearchForm,
    AddTrackForm,
    PlaylistForm,
    EditUserForm,
)
from models import db, connect_db, User, Song, Playlist, PlaylistSong, Like

import os, json

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

@app.route("/register", methods=["GET", "POST"])
def signup():
    """Handle user signup."""
    form = SignUpForm()
    if form.validate_on_submit():
        try:
            user = User.register(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
            )
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            if User.query.filter_by(username=form.username.data).first():
                flash("Username already taken", "danger")
            elif User.query.filter_by(email=form.email.data).first():
                flash("Email already taken", "danger")
            return render_template("register.html", form=form)

        do_login(user)
        flash(f"Welcome, maestro {user.username}!", "success")
        return redirect(f"/user")
    else:
        return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            do_login(user)
            return redirect(f"/user")
        flash("Invalid credentials.", "danger")
    return render_template("/user/login.html", form=form)


@app.route("/logout")
def logout():
    """Handle logout of user."""
    do_logout()
    flash("Logged out", "success")
    return redirect("/")


@app.route("/user")
def user_profile():
    """Show user profile."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    user = User.query.get_or_404(session[CURR_USER_KEY])
    playlists = Playlist.query.filter(Playlist.user_id == user.id).all()
    token = get_token()
    result = get_pop_recommendations(token)
    print(result)
    return render_template(
        "/user/user.html", user=user, playlists=playlists, result=result)


@app.route("/user/delete", methods=["POST"])
def delete_user():
    """Delete user."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(session[CURR_USER_KEY])
    db.session.delete(user)
    db.session.commit()
    do_logout()
    flash("User deleted", "success")
    return redirect("/")


@app.route("/user/edit", methods=["GET", "POST"])
def edit_user():
    """Edit user profile."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(session[CURR_USER_KEY])
    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        db.session.commit()
        flash("User updated", "success")
        return redirect(f"/user")
    else:
        return render_template("/user/edit_user.html", form=form, user=user)

# routes for music info

@app.route("/user/playlists", methods=["GET", "POST"])
def show_playlists():
    """Show user playlists."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(session[CURR_USER_KEY])
    playlists = Playlist.query.filter(Playlist.user_id == user.id).all()
    if request.method == "POST":
        data = request.get_json()
        playlist_name = request.form.get("playlist_name")
        playlist_description = request.form.get("playlist_description")
        print(f"data: {playlist_name}, {playlist_description}")
        if playlist_name:
            playlist = Playlist(
                name=playlist_name, user_id=user.id, description=playlist_description)
            db.session.add(playlist)
            db.session.commit()
            flash("Playlist created", "success")
            return redirect("/user/playlists")
    return render_template("/music/playlists.html", user=user, playlists=playlists)

@app.route("/user/playlists/add", methods=["POST"])
def add_song_to_playlist():
    """Add a song to a playlist."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(session[CURR_USER_KEY])

    data = request.get_json()
    playlist_name = data.get("playlist_name")
    playlist_description = data.get("playlist_description")
    track_id = data.get("track_id", None)
    playlist = Playlist(
        name=playlist_name, description=playlist_description, user_id=user.id
    )
    db.session.add(playlist)
    db.session.commit()
    # Add the song to the newly created playlist, only if a track_id is provided
    # if track_id is not None:
    token = get_token()
    result = get_audio_analysis(track_id, token)

    if Song.query.filter(Song.track_id == track_id).first():
        song = Song.query.filter(Song.track_id == track_id).first()
    else:
        song = Song.create_song(result)
        db.session.add(song)
        db.session.commit()

    playlist_song = PlaylistSong(
        playlist_id=playlist.id, song_id=song.id, user_id=user.id
    )
    db.session.add(playlist_song)
    db.session.commit()
    flash("Song added to playlist", "success")
    return redirect(f"/user/playlists/{playlist.id}")

@app.route("/user/playlists/<int:playlist_id>", methods=["GET", "POST"])
def show_playlist(playlist_id):
    """Show playlist."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = User.query.get_or_404(session[CURR_USER_KEY])
    playlist = Playlist.query.get_or_404(playlist_id)
    songs = PlaylistSong.query.filter(PlaylistSong.playlist_id == playlist_id).all()
    return render_template("/music/playlist.html", user=user, playlist=playlist, songs=songs)

@app.route("/search", methods=["GET", "POST"])
def search():
    """Search for songs on Spotify."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = User.query.get_or_404(session[CURR_USER_KEY])

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

@app.route("/get_albums/<artist_id>", methods=["GET", "POST"])
def get_artist_albums(artist_id):
    """Get albums from Spotify."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = User.query.get_or_404(session[CURR_USER_KEY])
    token = get_token()
    result = get_albums(artist_id, token)
    return render_template("/music/albums.html", result=result, user=user)


@app.route("/get_tracks/<album_id>", methods=["GET", "POST"])
def get_tracks(album_id):
    """Get tracks from Spotify."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    token = get_token()
    result = get_album_tracks(album_id, token)
    user = User.query.get_or_404(session[CURR_USER_KEY])
    playlists = [(playlist.id, playlist.name) for playlist in user.playlists]
    return render_template("/music/track_listing.html", result=result, user=user, playlists=playlists)


@app.route("/audio_analysis/<track_id>", methods=["GET", "POST"])
def audio_analysis(track_id):
    """Show audio analysis of song."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(session[CURR_USER_KEY])
    playlists = [(playlist.id, playlist.name) for playlist in user.playlists]

    token = get_token()
    result = get_audio_analysis(track_id, token)

    if request.method == "POST":
        data = request.get_json()
        playlist_id = data.get("playlist_id")
        print(playlist_id)
        print(track_id)
        if Song.query.filter(Song.track_id == track_id).first():
            song = Song.query.filter(Song.track_id == track_id).first()
        else:
            song = Song.create_song(result)
            db.session.add(song)
            db.session.commit()
        playlist_song = PlaylistSong(
            playlist_id=playlist_id, song_id=song.id, user_id=user.id
        )
        db.session.add(playlist_song)
        db.session.commit()
        flash("Song added to playlist", "success")
        return redirect(f"/user/playlists/{playlist_id}")
    else:
        return render_template("/music/audio_analysis.html",result=result,user=user,
        track_id=track_id,playlists=playlists,)

@app.route("/user/playlists/<int:playlist_id>/<track_id>", methods=["GET", "POST"])
def track_details(playlist_id, track_id):
    """Show track details."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = User.query.get_or_404(session[CURR_USER_KEY])
    playlist = Playlist.query.get_or_404(playlist_id)
    song = Song.query.filter(Song.track_id == track_id).first()
    return render_template("/music/song_details.html", user=user, playlist=playlist, song=song)

@app.route("/user/playlists/<int:playlist_id>/delete", methods=["POST"])
def delete_playlist(playlist_id):
    """Delete playlist."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    playlist = Playlist.query.get_or_404(playlist_id)
    db.session.delete(playlist)
    db.session.commit()
    flash("Playlist deleted.", "success")
    return redirect(f"/user/playlists")

@app.route("/user/playlists/<int:playlist_id>/<int:song_id>/delete", methods=["POST"])
def delete_song(playlist_id, song_id):
    """Delete song from playlist."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    playlist_song = PlaylistSong.query.filter(PlaylistSong.playlist_id == playlist_id, PlaylistSong.song_id == song_id).first()
    db.session.delete(playlist_song)
    db.session.commit()
    flash("Song deleted from playlist.", "success")
    return redirect(f"/user/playlists/{playlist_id}")

@app.route("/songs/<track_id>/like", methods=["POST"])
def like_song(track_id):
    """Like a song."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = User.query.get_or_404(session[CURR_USER_KEY])
    song = Song.query.filter_by(track_id=track_id).first()

    if not song:
        token = get_token()
        result = get_audio_analysis(track_id, token)
        song = Song.create_song(result)
        db.session.add(song)
        db.session.commit()

    like = Like.like_song(user.id, song.track_id)
    db.session.commit()
    
    return jsonify(message="Song liked!"), 200

@app.route("/songs/<track_id>/unlike", methods=["POST"])
def unlike_song(track_id):
    """Unlike a song."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = User.query.get_or_404(session[CURR_USER_KEY])
    song = Song.query.filter_by(track_id=track_id).first()

    if not song:
        token = get_token()
        result = get_audio_analysis(track_id, token)
        song = Song.create_song(result)
        db.session.add(song)
        db.session.commit()

    Like.unlike_song(user.id, song.track_id)
    db.session.commit()
    
    return jsonify(message="Song unliked!"), 200


@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""
    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers["Cache-Control"] = "public, max-age=0"
    return req
