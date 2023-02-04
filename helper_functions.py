from dotenv import load_dotenv
import os
import base64
from requests import post, get

load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

def get_token():

    auth_string = f'{client_id}:{client_secret}'
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': f'Basic {auth_base64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}
    result = post(url, headers=headers, data=data)
    token = result.json()['access_token']
    # return token


def get_auth_header(token):
    return {'Authorization' : f'Bearer {token}'}

def search_artist(artist_name, token):
    url = f'https://api.spotify.com/v1/search?q={artist_name}&type=artist&limit=1'
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = result.json()['artists']['items']
    if len(json_result) == 0:
        return None
    else:
        return json_result

    print(json_result)

def get_songs(artist_id, token):
    url = f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US'
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = result.json()['tracks']
    # return json_result

# token = get_token()
# res = search_artist('Metallica', token)
# artist_id = res[0]['id']
# songs = get_songs(artist_id, token)

# for song in songs:
#     print(song['name'])

# print(artist_id)
# print(res)