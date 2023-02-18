import os
from unittest import TestCase
from flask_bcrypt import Bcrypt

from models import db, User, Playlist, Song, PlaylistSong
bcrypt = Bcrypt()



os.environ['DATABASE_URL'] = "postgresql:///maestro-test"

from app import app



db.drop_all()
db.create_all()

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        PlaylistSong.query.delete()
        Song.query.delete()
        Playlist.query.delete()
        User.query.delete()

        self.client = app.test_client()
        u = User.register(username="testuser", password="testpassword", email="none@none.com")
        db.session.commit()
        self.u = u

    # def tearDown(self):
    #     """Clean up fouled transactions."""

    #     db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            username="testuser1",
            password="HASHED_PASSWORD1",
            email="none@none1.com",
        )

        db.session.add(u)
        db.session.commit()

        # User should exist in database
        self.assertEqual(len(User.query.all()), 2)
        self.assertEqual(u.username, "testuser1")
        self.assertEqual(u.email, "none@none1.com")
        

        db.session.rollback()


    def test_user_register(self):
        """Does register work?"""
        u = User.register(username="testuser1", password="testpassword1", email="none1@none.com")
        db.session.commit()
        self.assertEqual(len(User.query.all()), 2)
        self.assertEqual(u.username, "testuser1")
        self.assertEqual(u.email, "none1@none.com")
        # Bcrypt strings should start with $2b$
        self.assertTrue(u.password.startswith("$2b$"))

        db.session.rollback()

    def test_user_authenticate(self):
        """Does authenticate work?"""
        u = User.authenticate(username="testuser", password="testpassword")


        self.assertEqual(u.username, "testuser")

        self.assertFalse(User.authenticate(username="testuser", password="wrongpassword"))

        self.assertFalse(User.authenticate(username="wronguser", password="testpassword"))

        db.session.rollback()
        


    def test_playlist_model(self):
            """Does basic model work?"""
    
            p = Playlist(
                name="testplaylist",
                user_id=self.u.id
            )
    
            db.session.add(p)
            db.session.commit()
    
                # Playlist should exist in database
            self.assertEqual(len(Playlist.query.all()), 1)
            self.assertEqual(p.name, "testplaylist")
            self.assertEqual(p.user_id, self.u.id)
                
    
            db.session.rollback()

    def test_playlist_create_playlist(self):
        """Does create_playlist work?"""
        p = Playlist.create_playlist(name="testplaylist", description="testdescription", user_id=self.u.id)
        db.session.commit()
        
        self.assertEqual(p.name, "testplaylist")
        self.assertEqual(p.description, "testdescription")
        self.assertEqual(p.user_id, self.u.id)

        db.session.rollback()
        
    def test_playlist_song_model(self):
        """Does basic model work?"""

        s = Song(
            track_id="testtrackid",
            track_name="testsong",
            track_uri="testuri",
            artist_name="testartist",
            artist_id="testartistid",
        )

        db.session.add(s)
        db.session.commit()

        p = Playlist(
            name="testplaylist",
            user_id=self.u.id
        )

        db.session.add(p)
        db.session.commit()

        ps = PlaylistSong(
            playlist_id=p.id,
            song_id=s.id,
            user_id=self.u.id,
        )

        db.session.add(ps)
        db.session.commit()

        # PlaylistSong should exist in database
        self.assertEqual(len(PlaylistSong.query.all()), 1)
        self.assertEqual(ps.playlist_id, p.id)

        db.session.rollback()

    