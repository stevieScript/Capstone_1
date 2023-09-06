import unittest
from flask import Flask, g, session
import os
from models import db
from routes.playlists import playlist_bp
from models import User

os.environ['DATABASE_URL'] = "postgresql:///maestro-test"

from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['TESTING'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

db.drop_all()
db.create_all()

app.register_blueprint(playlist_bp)
db.init_app(app)
class PlaylistTestCase(unittest.TestCase):

    def setUp(self):

        self.client = app.test_client()

        with app.app_context():
            db.create_all()

        db.create_all(app=app)
        self.user = User(id=1, username='test', password='test1234', email='test@test.com') # Fill in necessary attributes
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.session.rollback()

    def test_show_playlists(self):
        with self.client.session_transaction() as session:
            g.user = self.user
        response = self.client.get('/playlists/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_add_song_to_playlist(self):
        with self.client.session_transaction() as session:
            g.user = self.user
        data = {"playlist_name": "My Playlist", "track_id": "12345"}
        response = self.client.post('playlists/add', json=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_show_playlist(self):
        with self.client.session_transaction() as session:
            g.user = self.user
        response = self.client.get('/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_track_details(self):
        with self.client.session_transaction() as session:
            g.user = self.user
        response = self.client.get('/1/12345',follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_delete_playlist(self):
        with self.client.session_transaction() as session:
            g.user = self.user
        response = self.client.delete('playlists/1/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_delete_song(self):
        with self.client.session_transaction() as session:
            g.user = self.user
        response = self.client.post('playlists/1/2/delete',follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
