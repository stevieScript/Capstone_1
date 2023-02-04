from app import db
from models import User, Song, Artist, ArtistSong, Playlist, PlaylistSong

db.drop_all()
db.create_all()

# Create users
user1 = User.register(username='testuser1', password='password', email='test1@test.com')

