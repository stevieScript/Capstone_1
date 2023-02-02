from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    """User in the system."""

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.String(20),
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.String(25),
        nullable=False,
    )

    email = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
    )

    user_img = db.Column(
        db.Text,
        default='https://www.pngitem.com/pimgs/m/146-1468479_my-profile-icon-blank-profile-picture-circle-hd.png'
    )
    
    playlists = db.relationship('Playlist', backref='user')

    def __repr__(self):
        return f'<User {self.id} {self.username} {self.email}>'

    @classmethod
    def register(cls, username, pwd, email, user_img):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8, email=email, user_img=user_img)

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.
        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False


class Playlist(db.Model):
    """Playlist in the system."""

    __tablename__ = "playlists"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String(20),
        nullable=False,
        unique=True,
    )

    description = db.Column(
        db.String(140)
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    user = db.relationship('User', backref='playlists')

    songs = db.relationship('Song', secondary='playlist_songs', backref='playlists')

    def __repr__(self):
        return f'<Playlist {self.id} {self.name} {self.description}>'

    @classmethod
    def create_playlist(cls, name, description, user_id):
        """Create playlist and return playlist."""

        return cls(name=name, description=description, user_id=user_id)


class Song(db.Model):
    """Song in the system."""

    __tablename__ = "songs"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    spotify_track_id = db.Column(
        db.String(20),
        nullable=False,
        unique=True,
    )

    track_name = db.Column(
        db.String(25),
        nullable=False,
        unique=True,
    )

    track_uri = db.Column(
        db.String(25),
        nullable=False,
        unique=True,
    )

    artist_name = db.Column(
        db.String(25),
        nullable=False,
        unique=True,
    )

    tempo = db.Column(
        db.Float,
        nullable=False,
    )

    time_signature = db.Column(
        db.Integer,
        nullable=False,
    )

    key = db.Column(
        db.Integer,
        nullable=False,
    )

    mode = db.Column(
        db.Integer,
        nullable=False,
    )

    duration_ms = db.Column(
        db.Integer,
        nullable=False,
    )

    loudness = db.Column(
        db.Float,
        nullable=False,
    )


    def __repr__(self):
        return f'<Song {self.id} {self.track_name} {self.artist_name}>'
    
    @classmethod
    def create_song(cls, spotify_track_id, track_name, track_uri, artist_name, tempo, time_signature, key, mode, duration_ms, loudness):
        """Create song and return song."""

        return cls(spotify_track_id=spotify_track_id, track_name=track_name, track_uri=track_uri, artist_name=artist_name, tempo=tempo, time_signature=time_signature, key=key, mode=mode, duration_ms=duration_ms, loudness=loudness)
    



class PlaylistSong(db.Model):
    """PlaylistSong in the system."""

    __tablename__ = "playlist_songs"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    playlist_id = db.Column(
        db.Integer,
        db.ForeignKey('playlists.id'),
        nullable=False
    )

    song_id = db.Column(
        db.Integer,
        db.ForeignKey('songs.id'),
        nullable=False
    )

    playlist = db.relationship('Playlist', backref='playlist_songs')
    song = db.relationship('Song', backref='playlist_songs')

    @classmethod
    def create_playlist_song(cls, playlist_id, song_id):
        """Create playlist_song and return playlist_song."""

        return cls(playlist_id=playlist_id, song_id=song_id)
    

class Artist(db.Model):
    """Artist in the system."""

    __tablename__ = "artists"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
    )

    spotify_artist_id = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
    )

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

    @classmethod
    def create_artist(cls, name, spotify_artist_id):
        """Create artist and return artist."""

        return cls(name=name, spotify_artist_id=spotify_artist_id)
    

class ArtistSong(db.Model):
    """ArtistSong in the system."""

    __tablename__ = "artist_songs"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    artist_id = db.Column(
        db.Integer,
        db.ForeignKey('artists.id'),
        nullable=False
    )

    song_id = db.Column(
        db.Integer,
        db.ForeignKey('songs.id'),
        nullable=False
    )

    artist = db.relationship('Artist', backref='artist_songs')
    song = db.relationship('Song', backref='artist_songs')

    def __repr__(self):
        return f'<ArtistSong {self.id} {self.artist_id} {self.song_id}>'

    @classmethod
    def create_artist_song(cls, artist_id, song_id):
        """Create artist_song and return artist_song."""

        return cls(artist_id=artist_id, song_id=song_id)


def connect_to_db(app):
    """Connect the database to our Flask app."""
    db.app = app
    db.init_app(app)

   


















def connect_db(app):
    """Connect this database to provided Flask app.
    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)