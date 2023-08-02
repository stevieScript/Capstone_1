from flask import Blueprint, render_template, redirect, flash, g
from models import User
from helper_functions import get_token, get_albums, get_album_tracks

albums_bp = Blueprint('albums', __name__, template_folder='templates', static_folder='static')

@albums_bp.route("/<artist_id>", methods=["GET", "POST"])
def get_artist_albums(artist_id):
    """Get albums from Spotify."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = User.query.get_or_404(g.user.id)
    token = get_token()
    result = get_albums(artist_id, token)
    return render_template("/music/albums.html", result=result, user=user)

@albums_bp.route("/songs/<album_id>", methods=["GET", "POST"])
def get_songs(album_id):
    """Get tracks from Spotify."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    token = get_token()
    result = get_album_tracks(album_id, token)
    user = User.query.get_or_404(g.user.id)
    playlists = [(playlist.id, playlist.name) for playlist in user.playlists]
    return render_template("/music/track_listing.html", result=result, user=user, playlists=playlists)