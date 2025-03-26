import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import os 
from dotenv import load_dotenv
from collections import defaultdict
import click
from tqdm import tqdm


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

# sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID,
#                                                            client_secret=SPOTIFY_CLIENT_SECRET))


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

for uri in tqdm(playlist_URIs):
    for track in sp.playlist_tracks(uri.split(":")[0])['items']:
        tracks[uri.split(":")[-1]].append(track['track']['name'])


@click.group()
def cli():
    pass
    

@cli.command()
def get_playlists():
    """Get the playlists of the current user"""
    click.echo("Here are your playlists:")
    for playlist in playlist_URIs:
        click.echo(playlist.split(":")[-1])


@cli.command()
@click.option('--name', prompt='Enter the name of the playlist you want to see the tracks of', help='The name of the playlist')
def get_tracks(name):
    """Get the tracks of a playlist. Make sure to copy and paste the URL that you were redirected to after running the app."""
    click.echo(f"Tracks from {name}:")
    for track in tracks[name]:
        click.echo(track)

def main():
    click.echo("Welcome to the Spotable CLI". center(50, "-"))

    value = click.prompt('What would you like to do: ', type=click.Choice(list(cli.commands.keys()) + ['exit']))
    click.echo('\n')
    click.echo("get_playlists: Get all playlists of the current user")
    click.echo("get_tracks: Get tracks of a playlist")
    while value != 'exit':  
        cli.commands[value]()
    
        if value == 'get-playlists':
            get_playlists()
            
        elif value == 'get-tracks':
            get_tracks()
            
        

if __name__ == '__main__':
    main()
