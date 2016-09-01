import requests
import base64
import secret

class SpotifyRouter(object):

    api_base_url = 'https://api.spotify.com/v1'
    accounts_base_url = 'https://accounts.spotify.com/api'

    client_id = secret.CLIENT_ID
    client_secret = secret.CLIENT_SECRET
    redirect_uri = secret.REDIRECT_URL

    scope = ' '.join(['user-read-private',
                      'user-read-email',
                      'user-top-read',
                      'playlist-modify-public',
                      'playlist-modify-private',
                      'playlist-read-private'])


    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.me = None

    def authenticate(self, code):
        self.access_token, self.refresh_token = self.get_access_token(code)

    def is_authenticated(self):
        return self.access_token and self.refresh_token

    def get_access_token(self, code):
        url = '{}/token'.format(self.accounts_base_url)
        request = requests.post(url, data = {
            'code': code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
            }, headers = {
                'Authorization': 'Basic {}'.format(base64.b64encode('{}:{}'
                    .format(self.client_id, self.client_secret)))
                })

        if request.status_code == 200:
            return request.json()['access_token'], request.json()['refresh_token']

        return None, None

    def get_playlists(self, user_id):
        if self.access_token:
            url = '{}/users/{}/playlists'.format(self.api_base_url, user_id)
            request = self.__get_request(url)

            if request.status_code == 200:
                return request.json()['items']

        return None

    def get_playlist(self, user_id, playlist_id):
        if self.access_token:
            url = '{}/users/{}/playlists/{}'.format(self.api_base_url, user_id, playlist_id)
            request = self.__get_request(url)

            if request.status_code == 200:
                return request.json()

        return None

    def create_playlist(self, user_id, playlist_name):
        if self.access_token:
            url = '{}/users/{}/playlists'.format(self.api_base_url, user_id)
            request = requests.post(url, json = { 'name': playlist_name },
                    headers = {
                        'Authorization': 'Bearer {}'.format(self.access_token),
                        'Content-Type': 'application/json'
                        })

            if request.status_code == 201:
                return request.json()

        return None

    def get_tracks_from_playlist(self, user_id, playlist_id):
        if self.access_token:
            url = '{}/users/{}/playlists/{}/tracks'.format(self.api_base_url, user_id, playlist_id)
            request = requests.get(url, headers = {
                'Authorization': 'Bearer {}'.format(self.access_token)
                })

            if request.status_code == 200:
                return [playlist_track['track'] for playlist_track in request.json()['items']]

        return None

    def get_recommendations_from_track(self, track_id):
        if self.access_token:
            url = '{}/recommendations'.format(self.api_base_url)
            request = requests.get(url, params = {
                'seed_tracks': [track_id],
                'target_danceability': 0.8,
                'limit': 5
                }, headers = {
                    'Authorization': 'Bearer {}'.format(self.access_token)
                    })

            if request.status_code == 200:
                return request.json()['tracks']

        return None

    def add_songs_to_playlist(self, user_id, playlist_id, track_uris):
        if self.access_token:
            url = '{}/users/{}/playlists/{}/tracks'.format(self.api_base_url, user_id, playlist_id)
            request = requests.post(url, json = { 'uris': track_uris }, headers = {
                'Authorization': 'Bearer {}'.format(self.access_token),
                'Content-Type': 'application/json'
                })

            if request.status_code == 201:
                return request.json()

        return None

    def get_me(self):
        if self.access_token:
            url = '{}/me'.format(self.api_base_url)
            request = requests.get(url, headers = {
                'Authorization': 'Bearer {}'.format(self.access_token)
                })

            if request.status_code == 200:
                self.me = request.json()
                return self.me

        return None

    def __get_request(self, url):
        return requests.get(url, headers = {
            'Authorization': 'Bearer {}'.format(self.access_token)
            })



