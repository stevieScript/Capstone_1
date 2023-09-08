import unittest
from unittest import TestCase
from unittest.mock import patch, Mock
from flask import Flask, g, session
import os
from models import db
from routes.albums import albums_bp
from models import User

os.environ['DATABASE_URL'] = "postgresql:///maestro-test"

from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['TESTING'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

db.drop_all()
db.create_all()

app.register_blueprint(albums_bp)
db.init_app(app)

class AlbumTestCase(unittest.TestCase):
      
      def setUp(self):
  
          self.client = app.test_client()
  
          with app.app_context():
              db.create_all()
  
          db.create_all(app=app)
          self.user = User(id=1, username='test', password='test1234', email='test@test.com')
          db.session.add(self.user)
          db.session.commit()

      def tearDown(self):
          db.session.remove()
          db.drop_all()
          db.session.rollback()

      def test_get_artist_albums(self):
          with self.client.session_transaction() as session:
              g.user = self.user
          response = self.client.get('/albums/12345', follow_redirects=True)
          self.assertEqual(response.status_code, 200)

      def test_get_songs(self):
          with self.client.session_transaction() as session:
              g.user = self.user
          response = self.client.get('/albums/songs/12345', follow_redirects=True)
          self.assertEqual(response.status_code, 200)
      
      def test_get_artist_albums_not_logged_in(self):
          response = self.client.get('/albums/12345', follow_redirects=True)
          self.assertEqual(response.status_code, 200)

      def test_get_songs_not_logged_in(self):
          response = self.client.get('/albums/songs/12345', follow_redirects=True)
          self.assertEqual(response.status_code, 200)

      

if __name__ == '__main__':
    unittest.main()
