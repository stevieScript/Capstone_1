from models import db
from app import app

db.drop_all()
db.create_all()

# Create users
# user1 = User.register(username='testuser1', password='password', email='test1@test.com')

# song1 = Song(track_id='asdfasdf', track_name='song1', track_uri='jnaskdjfn', artist_name='test', artist_id='1', album='asdf', album_art='qwerty', tempo=1.9, tempo_confidence=5,  duration=8, time_signature=4, time_signature_confidence=9, key='123', key_confidence=8, mode='Major', mode_confidence=7, loudness=7.7)

# pl = Playlist.create_playlist(name='test', description='test', user_id=1,)

# pls = PlaylistSong.create_playlist_song(playlist_id=1, song_id=1, user_id=1)
