# Capstone_1 MAESTRO
First capstone project for Springboard. 
https://capstone-maestro.herokuapp.com/

Maestro is and app for musicians that want to get audio analysis for their favorite songs using the Spotify API. 
You can create playlists based on different Key signatures that you are studying to keep practice fresh. 

1. Sign up.
2. Create a playlist to store your songs in.
3. Search for music by track name, artist or album. 
4. Add songs to playlist to filter them quickly for you practice sessions.

The Spotify API uses Oauth token for verification.

If you want to run the app locally:
<br>
'''python3 -m venv venv'''
<br>
'''source venv/bin/activate'''
<br>
'''pip install -r requirements.txt'''
<br>
'''createdb maestro'''
<br>
'''python3 seed.py'''
<br>
'''flask run'''
<br>
You will need to create a Spotify developer account and get a client id and client secret. To set up the environment variables, create a .env file in the root directory and add the following:

CLIENT_ID = 'your client id'
CLIENT_SECRET = 'your client secret'

Or you can set them in your terminal with the following commands:

'''export CLIENT_ID='your client id' '''

'''export CLIENT_SECRET='your client secret' '''
<br>

Link to Spotify API
https://developer.spotify.com/documentation/
