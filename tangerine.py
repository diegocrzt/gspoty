#!/usr/bin/env python
import json
import os
import sys

import spotipy
from gmusicapi import Mobileclient

keys_file = 'keys.json'
playlist_uri = sys.argv[1]
if not playlist_uri:
    print("usage: tangerine.py playlist_uri")
    exit(-1)

if not os.path.isfile(keys_file) or not os.access(keys_file, os.R_OK):
    print("There is no `key.json` to read client keys from")
    exit(-2)

with open(keys_file, 'r', encoding="UTF-8") as k:
    keys = json.load(k)

    for i in ['SPOTIPY_CLIENT_ID', 'SPOTIPY_CLIENT_SECRET', 'GOOGLE_MUSIC_DEVICE_ID']:
        os.environ[i] = keys[i]

gmapi = Mobileclient(debug_logging=False)
gmapi.oauth_login(os.environ['GOOGLE_MUSIC_DEVICE_ID'])

playlist_id = playlist_uri.split('/')[-1]
print("Working with this playlist " + playlist_id)

sp = spotipy.Spotify(client_credentials_manager=spotipy.SpotifyClientCredentials())
search_keys = []
try:
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
        search_key = "%s %s %s" % (track_name, album['name'], artists[0]['name'])
        search_keys.append(search_key)

except spotipy.SpotifyException as arg:
    print("Error trying to the list %s details: %s" % (playlist_id, str(arg)))
    exit(-3)

# GMusic part
playlists = gmapi.get_all_playlists()
playlist_in_gmusic = None
for p in playlists:
    if p['name'] == playlist_id:
        playlist_in_gmusic = p

if playlist_in_gmusic:
    print("The playlist already exists" + str(playlist_in_gmusic))
    exit(0)

g_music_playlist_id = gmapi.create_playlist(playlist_id, description="Imported from spotify", public=False)

for search_key in search_keys:
    r = gmapi.search(search_key, max_results=1)
    try:
        if r['song_hits']:
            found_track = r['song_hits'][0]['track']
            f_title = found_track['title']
            f_album = found_track['album']
            f_artist = found_track['artist']
            f_store_id = found_track['storeId']
            print("In GMusic %s %s %s (%s)" % (f_title, f_album, f_artist, f_store_id))
            gmapi.add_songs_to_playlist(g_music_playlist_id,f_store_id)
    except Exception as e:
        print("Something goes wrong with " + search_key)
        print("Details " + str(e))
