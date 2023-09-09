from flask import Blueprint, render_template, redirect, flash, g, request
from models import db, User, Playlist, PlaylistSong, Song
from helper_functions import get_token, get_audio_analysis

playlist_bp = Blueprint('playlists', __name__, template_folder='templates', static_folder='static')

@playlist_bp.route("/", methods=["GET", "POST"])
def show_playlists():
    """Show user playlists."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = g.user
    playlists = Playlist.query.filter(Playlist.user_id == user.id).all()
    if request.method == "POST":
        try:
            data = request.get_json()
            playlist_name = request.form.get("playlist_name")
            playlist_description = request.form.get("playlist_description")
            if playlist_name:
                playlist = Playlist(
                    name=playlist_name, user_id=user.id, description=playlist_description)
                db.session.add(playlist)
                db.session.commit()
                flash("Playlist created", "success")
                return render_template("/music/playlists.html", user=user, playlists=playlists), 200
        except:
            flash("Error occurred while creating the playlist", "danger")
            return render_template("/music/playlists.html", user=user, playlists=playlists), 500
    return render_template("/music/playlists.html", user=user, playlists=playlists), 200

@playlist_bp.route("/add", methods=["POST"])
def add_song_to_playlist():
    """Add a song to a playlist."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = g.user

    data = request.get_json()
    playlist_name = data.get("playlist_name")
    playlist_description = data.get("playlist_description")
    track_id = data.get("track_id")
    playlist = Playlist(
        name=playlist_name, description=playlist_description, user_id=user.id
    )
    db.session.add(playlist)
    db.session.commit()

    # Add the song to the newly created playlist, only if a track_id is provided
    if track_id is not None:
        token = get_token()
        result = get_audio_analysis(track_id, token)

        song = Song.query.filter(Song.track_id == track_id).first()
        if song is None:
            song = Song.create_song(result)
            db.session.add(song)

        playlist_song = PlaylistSong(
            playlist_id=playlist.id, song_id=song.id, user_id=user.id
        )
        db.session.add(playlist_song)

    try:
        db.session.commit()
    except:
        db.session.rollback()
        flash("Error occurred while adding the song to the playlist", "danger"), 500

    return redirect(f"/playlists/{playlist.id}"), 200

@playlist_bp.route("/<int:playlist_id>", methods=["GET", "POST"])
def show_playlist(playlist_id):
    """Show playlist."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    try:
        user = g.user
        playlist = Playlist.query.get_or_404(playlist_id)
        songs = PlaylistSong.query.filter(PlaylistSong.playlist_id == playlist_id).all()
        return render_template("/music/playlist.html", user=user, playlist=playlist, songs=songs), 200
    except:
        flash("Error occurred while showing the playlist", "danger")
        return redirect("/playlists"), 500
    
@playlist_bp.route("/<int:playlist_id>/<track_id>", methods=["GET", "POST", "DELETE"])
def track_details(playlist_id, track_id):
    """Show track details."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    try: 
        user = g.user
        playlist = Playlist.query.get_or_404(playlist_id)
        song = Song.query.filter(Song.track_id == track_id).first()
        return render_template("/music/song_details.html", user=user, playlist=playlist, song=song), 200
    except:
        flash("Error occurred while showing the track details", "danger")
        return redirect(f"/playlists/{playlist_id}"), 500

@playlist_bp.route("/<int:playlist_id>/delete", methods=["DELETE"])
def delete_playlist(playlist_id):
    """Delete playlist."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    try: 
        playlist = Playlist.query.get_or_404(playlist_id)
        db.session.delete(playlist)
        db.session.commit()
        return redirect(f"/playlists"), 200
    except:
        flash("Error occurred while deleting the playlist", "danger")
        return redirect(f"/playlists/{playlist_id}"), 500

@playlist_bp.route("/<int:playlist_id>/<int:song_id>/delete", methods=["POST"])
def delete_song(playlist_id, song_id):
    """Delete song from playlist."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    try:
        playlist_song = PlaylistSong.query.filter(PlaylistSong.playlist_id == playlist_id, PlaylistSong.song_id == song_id).first()
        db.session.delete(playlist_song)
        db.session.commit()
        return redirect(f"/playlists/{playlist_id}"), 200
    except:
        flash("Error occurred while deleting the song from the playlist", "danger")
        return redirect(f"/playlists/{playlist_id}/{song_id}"), 500