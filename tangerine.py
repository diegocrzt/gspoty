#!/usr/bin/env python
import json
import os
import sys

import spotipy

with open('keys.json', 'r', encoding="UTF-8") as k:
    keys = json.load(k)

    for i in ['SPOTIPY_CLIENT_ID', 'SPOTIPY_CLIENT_SECRET']:
        os.environ[i] = keys[i]

playlist_uri = sys.argv[1]
if not playlist_uri:
    print("usage: tangerine.py playlist_uri")
    exit(-1)

playlist_id = playlist_uri.split('/')[-1]
print("Working with this playlist " + playlist_id)

sp = spotipy.Spotify(client_credentials_manager=spotipy.SpotifyClientCredentials())
res = sp.playlist(playlist_id=playlist_id,
                  fields='tracks.items.track(album(id,name),artists(id,name),name,track_number,id)')
for t in res['tracks']['items']:
    track = t['track']
    album = track['album']
    artists = track['artists']
    track_name = track['name']
    track_number = track['track_number']
    track_id = track['id']
    print("%d - %s / %s (%s)" % (track_number, track_name, artists[0]['name'], track_id))
