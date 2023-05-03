from dotenv import load_dotenv
import os
import base64
from requests import post, get
import dotenv, csv


dotenv.load_dotenv('.env')

keys = ['C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B']

mode = ['Minor', 'Major']

client_id = os.environ.get('CLIENT_ID', os.getenv('CLIENT_ID'))
client_secret = os.environ.get('CLIENT_SECRET', os.getenv('CLIENT_SECRET'))

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


def get_albums(artist_id, token):
    url = f'https://api.spotify.com/v1/artists/{artist_id}/albums?market=US'
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = result.json()['items']
   
    album_set = set()
    album_list = []
    for item in json_result:
        id = item['id']
        release = item['release_date']
        name = item['name']
        
        album_key = f'{id}_{release}_{name}'
        if album_key not in album_set:
            album_set.add(album_key)
            album_art = item['images'][0]['url'] if len(item['images']) > 0 and item['images'][0]['url'] else 'https://example.com/default_album_art.jpg'
            album_list.append({
                'album_id': item['id'],
                'album_name': item['name'],
                'album_art': album_art,
                'artist_name': item['artists'][0]['name'],
                'artist_id': item['artists'][0]['id'],
                'release_date': item['release_date'],
                'total_tracks': item['total_tracks'],
                
            })

    return album_list

def get_genre_seeds(token):
    url = 'https://api.spotify.com/v1/recommendations/available-genre-seeds'
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = result.json()['genres']
    return json_result

def get_pop_recommendations(token):
    url = 'https://api.spotify.com/v1/recommendations?limit=10&seed_genres=pop'
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = result.json()['tracks']
    tracks = []
    for item in json_result:
        tracks.append({
            'track_id': item['id'],
            'track_name': item['name'],
            'track_uri': item['uri'],
            'artist_name': item['artists'][0]['name'],
            'artist_id': item['artists'][0]['id'],
            'album': item['album']['name'],
            'album_id': item['album']['id'],
            'album_art': item['album']['images'][0]['url']
        })
    return tracks

def get_album(album_id, token):
    url = f'https://api.spotify.com/v1/albums/{album_id}'
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = result.json()

    album = {
        'album_id': json_result['id'],
        'album_name': json_result['name'],
        'album_art': json_result['images'][0]['url'],
        'artist_name': json_result['artists'][0]['name'],
        'artist_id': json_result['artists'][0]['id'],
        'release_date': json_result['release_date'],
        'total_tracks': json_result['total_tracks'],
        'popularity': json_result['popularity']
    }

    return album

def get_album_tracks(album_id, token):
    url = f'https://api.spotify.com/v1/albums/{album_id}'
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = result.json()['tracks']['items']
    release_date = result.json()['release_date']
    popularity = result.json()['popularity']
    album_art = result.json()['images'][0]['url']
    tracks = []
    for item in json_result:
        tracks.append({
            'album_id': album_id,
            'album_name': item['name'],
            'album_art': album_art,
            'track_id': item['id'],
            'release_date': release_date,
            'track_name': item['name'],
            'track_uri': item['uri'],
            'artist_name': item['artists'][0]['name'],
            'artist_id': item['artists'][0]['id'],
            'duration': round(item['duration_ms'] / 60000, 2),
            'explicit': item['explicit'],
            'track_number': item['track_number'],
            'popularity': popularity
        })
    return tracks

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
        'album_id': json_result['album']['id'],
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
    return analysis
    

def generic_search(search_type, search_term, token):
    default_image = 'https://images.unsplash.com/photo-1601066525716-3cca33c6d4c6?ixlib=rb-4.0.3&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1050&q=80'
    
    url = f'https://api.spotify.com/v1/search?q={search_term}&type={search_type}&limit=10'
    headers = get_auth_header(token)

    search_result = get(url, headers=headers)


    result = []
    
    if search_type == 'track':
        for item in search_result.json()['tracks']['items']:
            
            if len(item['album']['images']) == 0:
                item['album']['images'].append({'url': default_image})
            result.append({
                'name': item['name'],
                'artist': item['artists'][0]['name'],
                'artist_id': item['artists'][0]['id'],
                'album': item['album']['name'],
                'album_id': item['album']['id'],
                'id': item['id'],
                'type': 'track',
                'image': item['album']['images'][0]['url']
            })
    elif search_type == 'artist':
        for item in search_result.json()['artists']['items']:
           
            if len(item['images']) == 0:
                item['images'].append({'url': default_image})
            result.append({
                'name': item['name'],
                'id': item['id'],
                'image': item['images'][0]['url'],
                'type': 'artist',
            })

    elif search_type == 'album':
        for item in search_result.json()['albums']['items']:
           
            if len(item['images']) == 0:
                item['images'].append({'url': default_image})
            result.append({
                'image': item['images'][0]['url'],
                'name': item['name'],
                'artist': item['artists'][0]['name'],
                'artist_id': item['artists'][0]['id'],
                'id': item['id'],
                'type': 'album',
            })

    return result

