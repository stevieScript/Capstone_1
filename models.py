from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

# db.drop_all()
# db.create_all()

class User(db.Model):
    """User in the system."""

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    # user_img = db.Column(
    #     db.Text
    #     # default='https://www.pngitem.com/pimgs/m/146-1468479_my-profile-icon-blank-profile-picture-circle-hd.png'
    # )
    
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

        
    @classmethod
    # method to add song to song table, if it's not already there, and playlist_songs table. Or, add song to playlist_songs table if it's already in the song table
    def add_song(cls, song, playlist_id):
        """Add song to playlist."""

        # check if song is already in songs table
        song = Song.query.filter_by(song_id=song['id']).first()
        # if song is not in songs table, add it
        if not song:
            song = Song.create_song(song)
            db.session.add(song)
            db.session.commit()
        # add song to playlist_songs table
        playlist_song = PlaylistSong(playlist_id=playlist_id, song_id=song.id) 
        db.session.add(playlist_song)
        db.session.commit()
        return song
    
    @classmethod
    # method to remove song from playlist_songs table
    def remove_song(cls, song_id, playlist_id):
        """Remove song from playlist."""

        # remove song from playlist_songs table
        playlist_song = PlaylistSong.query.filter_by(playlist_id=playlist_id, song_id=song_id).first()
        db.session.delete(playlist_song)
        db.session.commit()
        return playlist_song



class Playlist(db.Model):
    """Playlist in the system."""

    __tablename__ = "playlists"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    description = db.Column(
        db.String(140)
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    songs = db.relationship('Song', secondary='playlist_songs', backref='songs')

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
        autoincrement=True,
    )

    track_id = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    track_name = db.Column(
        db.Text,
        nullable=False,
    )

    track_uri = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    artist_name = db.Column(
        db.Text,
        nullable=False,
    )

    artist_id = db.Column(
        db.Text,
        nullable=False,
    )

    album = db.Column(
        db.Text,
        nullable=False,
    )

    album_art = db.Column(
        db.Text,
        nullable=False,
    )

    tempo = db.Column(
        db.Float,
        nullable=False,
    )

    tempo_confidence = db.Column(
        db.Integer,
        nullable=False,
    )

    time_signature = db.Column(
        db.Integer,
        nullable=False,
    )

    time_signature_confidence = db.Column(
        db.Integer,
        nullable=False,
    )

    key = db.Column(
        db.Text,
        nullable=False,
    )

    key_confidence = db.Column(
        db.Integer,
        nullable=False,
    )

    mode = db.Column(
        db.Text,
        nullable=False,
    )

    mode_confidence = db.Column(
        db.Integer,
        nullable=False,
    )

    duration = db.Column(
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

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True, 
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

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    playlist = db.relationship('Playlist', backref='playlist_songs')
    song = db.relationship('Song', backref='playlist_songs')

    @classmethod
    def create_playlist_song(cls, playlist_id, song_id, user_id):
        """Create playlist_song and return playlist_song."""

        return cls(playlist_id=playlist_id, song_id=song_id)
    

# class Artist(db.Model):
#     """Artist in the system."""

#     __tablename__ = "artists"

#     id = db.Column(
#         db.Integer,
#         primary_key=True,
#         autoincrement=True,
#     )

#     name = db.Column(
#         db.Text,
#         nullable=False,
#         unique=True,
#     )

#     spotify_artist_id = db.Column(
#         db.Text,
#         nullable=False,
#         unique=True,
#     )

#     def __repr__(self):
#         return f'<Artist {self.id} {self.name}>'

#     @classmethod
#     def create_artist(cls, name, spotify_artist_id):
#         """Create artist and return artist."""

#         return cls(name=name, spotify_artist_id=spotify_artist_id)
    

# class ArtistSong(db.Model):
#     """ArtistSong in the system."""

#     __tablename__ = "artist_songs"

#     id = db.Column(
#         db.Integer,
#         primary_key=True,
#         autoincrement=True,
#     )

#     artist_id = db.Column(
#         db.Integer,
#         db.ForeignKey('artists.id'),
#         nullable=False
#     )

#     song_id = db.Column(
#         db.Integer,
#         db.ForeignKey('songs.id'),
#         nullable=False
#     )

#     artist = db.relationship('Artist', backref='artist_songs')
#     # song = db.relationship('Song', backref='artist_songs')

#     def __repr__(self):
#         return f'<ArtistSong {self.id} {self.artist_id} {self.song_id}>'

#     @classmethod
#     def create_artist_song(cls, artist_id, song_id):
#         """Create artist_song and return artist_song."""

#         return cls(artist_id=artist_id, song_id=song_id)



def connect_db(app):
    """Connect this database to provided Flask app.
    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)