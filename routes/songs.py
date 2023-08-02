from flask import Blueprint, jsonify, request, redirect, flash, g, render_template
from models import db, Song, User, Like, PlaylistSong
from helper_functions import get_token, get_audio_analysis
songs_bp = Blueprint('songs', __name__, template_folder='templates', static_folder='static')

@songs_bp.route("/<track_id>", methods=["GET", "POST"])
def song_details(track_id):
    """Show audio analysis of song."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(g.user.id)
    playlists = [(playlist.id, playlist.name) for playlist in user.playlists]

    token = get_token()
    result = get_audio_analysis(track_id, token)

    if request.method == "POST":
        try:
            data = request.get_json()
            playlist_id = data.get("playlist_id")
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
            return redirect(f"user/playlists/{playlist_id}"), 200
        except:
            flash("Something went wrong. Please try again.", "danger")
            return redirect("/")
    else:
        return render_template("/music/audio_analysis.html",result=result,user=user,
        track_id=track_id,playlists=playlists,)

@songs_bp.route("/<track_id>/like", methods=["POST"])
def like_song(track_id):
    """Like a song."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = User.query.get_or_404(g.user.id)
    song = Song.query.filter_by(track_id=track_id).first()
    try:
        if not song:
            token = get_token()
            result = get_audio_analysis(track_id, token)
            song = Song.create_song(result)
            db.session.add(song)
            db.session.commit()

        like = Like.like_song(user.id, song.track_id)
        db.session.commit()

        return jsonify(message="Song liked!"), 200
    except:
        flash("Something went wrong. Please try again.", "danger")
        return redirect("/")

@songs_bp.route("/<track_id>/unlike", methods=["POST"])
def unlike_song(track_id):
    """Unlike a song."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    try:
        user = User.query.get_or_404(g.user.id)
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
    except:
        flash("Something went wrong. Please try again.", "danger")
        return redirect("/")