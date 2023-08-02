import os
from unittest import TestCase

from models import db, User, Playlist, Song, PlaylistSong

os.environ['DATABASE_URL'] = "postgresql:///maestro-test"

from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['TESTING'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

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

            resp = c.get(f"/user/")

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.u.username, str(resp.data))

    def test_show_playlist(self):
        """Does show playlist page work?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id

            resp = c.get(f"/playlists/")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Create Playlist', str(resp.data))


    def test_show_search(self):
        """Does show search page work?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id

            resp = c.get(f"/search")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Search', str(resp.data))

    def test_song_details(self):
        """Does audio analysis page work?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id

            resp = c.get(f"/songs/{self.track_id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Analysis', str(resp.data))

    def test_add_track_to_playlist(self):
        """Does add track to playlist page work?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id

            resp = c.get(f"/songs/{self.track_id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Add song', str(resp.data))

    def test_add_playlist(self):
        """Does add playlist page work?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id

            resp = c.get(f"/playlists/")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Create Playlist', str(resp.data))

    def test_get_songs(self):
        """Does get tracks page work?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id

            resp = c.get(f"/search")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Search', str(resp.data))

    def test_delete_playlist(self):
        """Does delete playlist page work?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id

            p = Playlist(name="test", user_id=self.u.id)
            db.session.add(p)
            db.session.commit()

            resp = c.post(f"/playlists/{p.id}", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Search', str(resp.data))

            # Check if the playlist was deleted from the database
            playlist = Playlist.query.get(p.id)
            self.assertIsNone(playlist)


    def test_delete_track(self):
        """Does delete track page work?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id

            p = Playlist(name="test", user_id=self.u.id)
            db.session.add(p)
            db.session.commit()

            s = Song(track_id=self.track_id, track_name="testname", track_uri='testuri', artist_name="test", artist_id="test")
            db.session.add(s)
            db.session.commit()

            ps = PlaylistSong(playlist_id=p.id, song_id=s.id, user_id=self.u.id)
            db.session.add(ps)
            db.session.commit()

            resp = c.post(f"/playlists/1/1/delete", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Playlist', str(resp.data))

            db.session.delete(ps)
            db.session.delete(p)
            db.session.delete(s)

    def test_logout(self):
        """Does logout page work?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id

            resp = c.get(f"/user/logout", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Login', str(resp.data))