import os
from unittest import TestCase

from models import db, User, Playlist, Song, PlaylistSong

os.environ['DATABASE_URL'] = "postgresql:///maestro-test"

from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['TESTING'] = True

db.drop_all()
db.create_all()

class UserViewTestCase(TestCase):
    """Test views for user routes."""

    def setUp(self):
        """Create test client, add sample data."""

        PlaylistSong.query.delete()
        Song.query.delete()
        Playlist.query.delete()
        User.query.delete()

        self.client = app.test_client()
        u = User.register(username="testuser", password="testpassword", email="none@none.com")
        db.session.commit()

        track_id = '6y0igZArWVi6Iz0rj35c1Y'
        self.u = u
        self.track_id = track_id

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_user_profile(self):
        """Does user profile page work?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id

            resp = c.get(f"/user/{self.u.id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.u.username, str(resp.data))

    def test_show_playlist(self):
        """Does show playlist page work?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id

            resp = c.get(f"/user/{self.u.id}/playlists")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Create Playlist', str(resp.data))


    def test_show_search(self):
        """Does show search page work?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id

            resp = c.get(f"/user/{self.u.id}/search")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Search', str(resp.data))

    def test_audio_analysis(self):
        """Does audio analysis page work?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id

            resp = c.get(f"/audio_analysis/{self.u.id}/{self.track_id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Analysis', str(resp.data))

    def test_add_track_to_playlist(self):
        """Does add track to playlist page work?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id

            resp = c.get(f"/audio_analysis/{self.u.id}/{self.track_id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Add song', str(resp.data))

    def test_add_playlist(self):
        """Does add playlist page work?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id

            resp = c.get(f"/user/{self.u.id}/playlists")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Create Playlist', str(resp.data))

    def test_get_tracks(self):
        """Does get tracks page work?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id

            resp = c.get(f"/user/{self.u.id}/search")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Search', str(resp.data))
