from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    """User in the system."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True,)
    username = db.Column(db.Text, nullable=False, unique=True,)
    password = db.Column(db.Text, nullable=False,)
    email = db.Column(db.Text, nullable=False, unique=True,)
    playlists = db.relationship('Playlist', backref='user')

    def __repr__(self):
        return f'<User {self.id} {self.username} {self.email}>'
    
    @classmethod
    def register(cls, username, password, email):
        """Register user w/hashed password & return user."""
        hashed = bcrypt.generate_password_hash(password).decode('UTF-8')
        user = User(username=username, password=hashed, email=email)
        db.session.add(user)
        # return instance of user w/username and hashed password
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Validate that user exists & password is correct.
        Return user if valid; else return False.
        """
        u = User.query.filter_by(username=username).first()
        if u and bcrypt.check_password_hash(u.password, password):
            # return user instance
            return u
        else:
            return False
        
    def is_liked(self, track_id):
        like = Like.query.filter_by(user_id=self.id, song_id=track_id).first()
        return like is not None
class Playlist(db.Model):
    """Playlist in the system."""

    __tablename__ = "playlists"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True,)
    name = db.Column(db.Text, nullable=False,)
    description = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
    songs = db.relationship('Song', secondary='playlist_songs', backref='songs')
    playlist_songs = db.relationship('PlaylistSong', backref='playlist', cascade="all, delete" )

    def __repr__(self):
        return f'<Playlist {self.id} {self.name} {self.description}>'

    @classmethod
    def create_playlist(cls, name, description, user_id):
        """Create playlist and return playlist."""
        return cls(name=name, description=description, user_id=user_id)
class Song(db.Model):
    """Song in the system."""

    __tablename__ = "songs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True,)
    track_id = db.Column(db.Text, nullable=False, unique=True)
    track_name = db.Column(db.Text, nullable=False,)
    track_uri = db.Column(db.Text, nullable=False, unique=True,)
    artist_name = db.Column(db.Text, nullable=False)
    artist_id = db.Column(db.Text, nullable=False)
    album = db.Column(db.Text)
    album_art = db.Column(db.Text)
    tempo = db.Column(db.Float)
    tempo_confidence = db.Column(db.Integer)
    time_signature = db.Column(db.Integer)
    time_signature_confidence = db.Column(db.Integer)
    key = db.Column(db.Text)
    key_confidence = db.Column(db.Integer)
    mode = db.Column(db.Text)
    mode_confidence = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    loudness = db.Column(db.Float)

    def __repr__(self):
        return f'<Song {self.id} {self.track_name} {self.artist_name}>'
    
    @classmethod
    # methods that accepts a dictionary of song attributes and creates a song instance
    def create_song(cls, song_dict):
        """Create song and return song."""

        return cls(track_id=song_dict['track_id'], track_name=song_dict['track_name'], track_uri=song_dict['track_uri'], artist_name=song_dict['artist_name'], artist_id=song_dict['artist_id'], tempo=song_dict['tempo'], album=song_dict['album'], tempo_confidence=song_dict['tempo_confidence'],time_signature=song_dict['time_signature'], time_signature_confidence=song_dict['time_signature_confidence'], key=song_dict['key'], key_confidence=song_dict['key_confidence'], mode=song_dict['mode'], mode_confidence=song_dict['mode_confidence'], duration=song_dict['duration'], loudness=song_dict['loudness'], album_art=song_dict['album_art'])

    @classmethod
    # methods that will query the db to see if the song already exists, and if it does, return the song instance. If it doesn't, create a song instance and return it
    def get_song(cls, song_id):
        """Get song from database."""
        song = Song.query.filter_by(track_id=song_id).first()
        if song:
            return song
        else:
            return None
class PlaylistSong(db.Model):
    """PlaylistSong in the system."""

    __tablename__ = "playlist_songs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'))
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song = db.relationship('Song', backref='playlist_songs')

    @classmethod
    def create_playlist_song(cls, playlist_id, song_id, user_id):
        """Create playlist_song and return playlist_song."""
        return cls(playlist_id=playlist_id, song_id=song_id, user_id=user_id)
    
class Like(db.Model):
    """Like in the system."""

    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True,)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_id = db.Column(db.Text, db.ForeignKey('songs.track_id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='likes')
    song = db.relationship('Song', backref='likes')

    def __repr__(self):
        return f'<Like {self.id} user={self.user_id} song={self.song_id}>'

    @classmethod
    def like_song(cls, user_id, track_id):
        """Create like and return like."""
        like = cls(user_id=user_id, song_id=track_id)
        db.session.add(like)
        return like

    @classmethod
    def unlike_song(cls, user_id, track_id):
        """Remove a like."""
        like = cls.query.filter_by(user_id=user_id, song_id=track_id).first()
        if like:
            db.session.delete(like)

   


def connect_db(app):
    """Connect this database to provided Flask app.
    You should call this in your Flask app.
    """
    db.app = app
    db.init_app(app)