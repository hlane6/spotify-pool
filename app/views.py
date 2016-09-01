from flask import render_template, request, make_response, redirect, session
from app import app
from utils import generateRandomString
import urllib
import requests
import base64
import datetime
import more_itertools
from spotify import SpotifyRouter
import secret

stateKey = 'spotify_auth_state'

spotify_router = SpotifyRouter()

@app.route('/')
def index():
    if spotify_router.is_authenticated():
        if not spotify_router.me:
            spotify_router.get_me()

        my_playlists = spotify_router.get_playlists(spotify_router.me['id'])

        if my_playlists:
            return render_template('index.html',
                    user = spotify_router.me['display_name'],
                    playlists = my_playlists)
        return render_template('index.html',
                user = spotify_router.me['display_name'],
                playlists = session['playlists'])

    return render_template('index.html')

@app.route('/login')
def login():
    state = generateRandomString(16)

    resp = redirect('https://accounts.spotify.com/authorize?' +
            urllib.urlencode({
                'response_type': 'code',
                'client_id': secret.CLIENT_ID,
                'scope': SpotifyRouter.scope,
                'redirect_uri': secret.REDIRECT_URL,
                'state': state
                }))

    resp.set_cookie(stateKey, state)
    return resp

@app.route('/callback')
def callback():
    code = request.args['code']
    state = request.args['state']
    storedState = request.cookies[stateKey]

    if not state or state != storedState:
        return redirect('/#' +
                urllib.urlencode({
                    'error': 'state_mismatch'
                    }))
    else:
        spotify_router.authenticate(code)
        if spotify_router.is_authenticated():
            me = spotify_router.get_me()

            if me:
                session['user_id'] = me['id']
                session['display_name'] = me['display_name']

                my_playlists = spotify_router.get_playlists(me['id'])

                if my_playlists:
                    return render_template('index.html',
                            user = spotify_router.me['display_name'],
                            playlists = my_playlists)

                return render_template('index.html',
                        user = session['display_name'])

        return redirect('/#' +
                urllib.urlencode({
                    'error': 'invalid_token'
                    }))

@app.route('/playlists/<user>/<id>')
def playlist(user, id):
    if spotify_router.me and spotify_router.is_authenticated():
        playlist = spotify_router.get_playlist(user, id)
        tracks = spotify_router.get_tracks_from_playlist(user, id)

        if playlist and tracks:
            mini_playlist = {
                    'id': id,
                    'name': playlist['name'],
                    'owner': playlist['owner'],
                    'tracks': tracks
                    }

            return render_template('playlist.html',
                    user = spotify_router.me['display_name'],
                    playlist = mini_playlist)

    return redirect('/login')

@app.route('/features/<id>')
def features(id):
    access_token = session['access_token']
    if access_token:
        r = requests.get('https://api.spotify.com/v1/audio-features/' + id,
                headers = {
                    'Authorization': 'Bearer ' + access_token
                    })
        return render_template('features.html',
                features=r.json())
    return redirect('/')

@app.route('/playlists/<user>/<id>/pool')
def pool(user, id):
    if spotify_router.is_authenticated():
        playlist_tracks = spotify_router.get_tracks_from_playlist(user, id)

        tracks = []
        me = 'thebartoge'
        playlist_name = 'Pool - ' + str(datetime.datetime.now())

        created_playlist = spotify_router.create_playlist(me, playlist_name)

        if created_playlist:
            for track in playlist_tracks:
                recommendations = spotify_router.get_recommendations_from_track(track['id'])

                for recommendation in recommendations:
                    tracks.append(recommendation)

            for chunk in more_itertools.chunked(tracks, 100):
                uris = [track['uri'] for track in chunk]
                spotify_router.add_songs_to_playlist(user, created_playlist['id'], uris)

            playlist = {
                    'id': created_playlist['id'],
                    'name': created_playlist['name'],
                    'owner': created_playlist['owner'],
                    'tracks': tracks
                    }

            return render_template('playlist.html',
                    user = spotify_router.me['display_name'],
                    playlist = playlist)
    return redirect('/')


