import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os 
from dotenv import load_dotenv
from collections import defaultdict
import click


# Load environment variables
load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# Authenticate with Spotify
scope = "playlist-read-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                                               client_secret=SPOTIFY_CLIENT_SECRET,
                                               redirect_uri=SPOTIFY_REDIRECT_URI,
                                               scope=scope))


# Get current user
current_user = sp.me()['uri'].split(":")[-1]


# Get the user's playlists
playlist_URIs =[]
playlists = sp.user_playlists(user=current_user)
while playlists:
    for i, playlist in enumerate(playlists['items']):
        # print(f"{i + 1 + playlists['offset']:4d} {playlist['uri']} {playlist['name']}")
        playlist_URIs.append(playlist['uri'].split(':')[2] + ":" + playlist['name'])
    if playlists['next']:
        playlists = sp.next(playlists)
    else:
        playlists = None


tracks = defaultdict(list)

for uri in playlist_URIs:
    for track in sp.playlist_tracks(uri.split(":")[0])['items']:
        tracks[uri.split(":")[-1]].append(track['track']['name'])



@click.command()
@click.option('--name', prompt='Enter the name of the playlist you want to see the tracks of', help='The name of the playlist')

def get_tracks(name):
    click.echo(f"Tracks in {name}:")
    for track in tracks[name]:
        click.echo(track)

if __name__ == '__main__':
    get_tracks()

