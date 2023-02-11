from dotenv import load_dotenv
import os
import base64
from requests import post, get
import dotenv
from models import db, connect_db, User, Song, Artist, ArtistSong, Playlist, PlaylistSong

dotenv.load_dotenv('.env')

keys = ['C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B']

mode = ['Minor', 'Major']

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
    return token


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
    
def get_artist_id(artist_name, token):
    url = f'https://api.spotify.com/v1/search?q={artist_name}&type=artist&limit=1'
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = result.json()['artists']['items']
    if len(json_result) == 0:
        return None
    else:
        return json_result[0]['id']
    
def get_track_id(track_name, token):
    url = f'https://api.spotify.com/v1/search?q={track_name}&type=track&limit=1'
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = result.json()['tracks']['items']
    if len(json_result) == 0:
        return None
    else:
        return json_result[0]['id']

def get_songs(artist_id, token):
    url = f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US'
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = result.json()['tracks']
    return json_result

def get_albums(artist_id, token):
    url = f'https://api.spotify.com/v1/artists/{artist_id}/albums'
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = result.json()['items']
    return json_result

def get_album(album_id, token):
    url = f'https://api.spotify.com/v1/albums/{album_id}'
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = result.json()
    return json_result

def get_album_tracks(album_id, token):
    url = f'https://api.spotify.com/v1/albums/{album_id}/tracks'
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = result.json()['items']
    return json_result

def get_album_art(album_id, token):
    url = f'https://api.spotify.com/v1/albums/{album_id}'
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = result.json()['images'][0]['url']
    return json_result

def get_track_info(track_id, token):
    url = f'https://api.spotify.com/v1/tracks/{track_id}'
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = result.json()

    track_info = {
        'track_id': json_result['id'],
        'track_name': json_result['name'],
        'track_uri': json_result['uri'],
        'artist_name': json_result['artists'][0]['name'],
        'artist_id': json_result['artists'][0]['id'],
        'album': json_result['album']['name'],
        'album_art': json_result['album']['images'][0]['url']
    }

    return track_info
    
def get_audio_analysis(track_id, token):
    url = f'https://api.spotify.com/v1/audio-analysis/{track_id}'
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    data = result.json()['track']
    analysis = {
            'duration': round(data['duration'] / 60, 2),
            'key': keys[data['key']],
            'key_confidence': round(data['key_confidence'] * 100),
            'mode': mode[data['mode']],
            'mode_confidence': round(data['mode_confidence'] * 100),
            'time_signature': data['time_signature'],
            'time_signature_confidence': round(data['time_signature_confidence'] * 100),
            'tempo': round(data['tempo']),
            'tempo_confidence': round(data['tempo_confidence'] * 100),
            'loudness': data['loudness'],
        }
    track_info = get_track_info(track_id, token)
    analysis.update(track_info)
    print(analysis)
    return analysis
    

def generic_search(search_type, search_term, token):
    url = f'https://api.spotify.com/v1/search?q={search_term}&type={search_type}&limit=10'
    headers = get_auth_header(token)

    search_result = get(url, headers=headers)

    result = []
    
    if search_type == 'track':
        for item in search_result.json()['tracks']['items']:
            result.append({
                'name': item['name'],
                'artist': item['artists'][0]['name'],
                'album': item['album']['name'],
                'id': item['id'],
                'type': 'track',
                'image': item['album']['images'][0]['url']
                
            })
    elif search_type == 'artist':
        for item in search_result.json()['artists']['items']:
            result.append({
                'name': item['name'],
                'id': item['id'],
                'type': 'artist',
                'image': item['images'][0]['url']
            })

    elif search_type == 'album':
        for item in search_result.json()['albums']['items']:
            result.append({
                'image': item['images'][0]['url'],
                'name': item['name'],
                'artist': item['artists'][0]['name'],
                'id': item['id'],
                'type': 'album'
            })

    return result

    # return json_result

# def add_to_playlist(track_id, playlist_id, user_id):
    




#     return result

# token = get_token()
# res = search_artist('Metallica', token)
# artist_id = res[0]['id']
# songs = get_songs(artist_id, token)

# for song in songs:
#     print(song['name'])

# print(artist_id)
# print(res)