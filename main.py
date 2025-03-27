import spotipy 
from spotipy.oauth2 import SpotifyOAuth 
import os 
from dotenv import load_dotenv 
from collections import defaultdict
import click 
from tqdm import tqdm 
from utils import capture_redirect



# Load environment variables
load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

def setup_auth():
    # Authenticate with Spotify

    scope = "playlist-read-private"
    auth_manager = SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                                client_secret=SPOTIFY_CLIENT_SECRET,
                                redirect_uri=SPOTIFY_REDIRECT_URI,
                                scope=scope)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    # Get current user
    current_user = sp.me()['uri'].split(":")[-1]

    result = [sp, current_user]

    return result

def setup_app(auth):
    # Get the user's playlists
    sp = auth[0]
    current_user = auth[1]
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

    return playlist_URIs, tracks


@click.group()
def cli():
    pass
    

@cli.command()
def get_playlists(playlist_URIs):
    """Get the playlists of the current user"""
    click.echo("Here are your playlists:")
    for playlist in playlist_URIs:
        click.echo(playlist.split(":")[-1])


@cli.command()
@click.option('--name', prompt='Enter the name of the playlist you want to see the tracks of', help='The name of the playlist')
def get_tracks(tracks, name):
    """Get the tracks of a playlist. Make sure to copy and paste the URL that you were redirected to after running the app."""
    click.echo(f"Tracks from {name}:")
    for track in tracks[name]:
        click.echo(track)

def main():
    # click.echo("Welcome to the SoundPort CLI". center(50, "-"))
    # click.echo("If this is your first time using this app, you will be redirected to a webpage to authenticate with Spotify.")
    # click.echo("Copy and paste the URL you are redirected to in the terminal.")
    # click.echo("\n")
    # # click.echo("You have been authenticated successfully!")
    # # click.echo("Here are the commands you can use: ")   
    # # click.echo("get_playlists: Get all playlists of the current user")
    # # click.echo("get_tracks: Get tracks of a playlist"))

    click.echo("""
                                                                                                                        
                                                          ,-.----.                                  
  .--.--.                                                 \    /  \                         ___     
 /  /    '.                                          ,---,|   :    \                      ,--.'|_   
|  :  /`. /    ,---.           ,--,      ,---,     ,---.'||   |  .\ :   ,---.    __  ,-.  |  | :,'  
;  |  |--`    '   ,'\        ,'_ /|  ,-+-. /  |    |   | :.   :  |: |  '   ,'\ ,' ,'/ /|  :  : ' :  
|  :  ;_     /   /   |  .--. |  | : ,--.'|'   |    |   | ||   |   \ : /   /   |'  | |' |.;__,'  /   
 \  \    `. .   ; ,. :,'_ /| :  . ||   |  ,"' |  ,--.__| ||   : .   /.   ; ,. :|  |   ,'|  |   |    
  `----.   \'   | |: :|  ' | |  . .|   | /  | | /   ,'   |;   | |`-' '   | |: :'  :  /  :__,'| :    
  __ \  \  |'   | .; :|  | ' |  | ||   | |  | |.   '  /  ||   | ;    '   | .; :|  | '     '  : |__  
 /  /`--'  /|   :    |:  | : ;  ; ||   | |  |/ '   ; |:  |:   ' |    |   :    |;  : |     |  | '.'| 
'--'.     /  \   \  / '  :  `--'   \   | |--'  |   | '/  ':   : :     \   \  / |  , ;     ;  :    ; 
  `--'---'    `----'  :  ,      .-./   |/      |   :    :||   | :      `----'   ---'      |  ,   /  
                       `--`----'   '---'        \   \  /  `---'.|                          ---`-'   
                                                 `----'     `---`                                   
                                                                                                    
           
    Welcome to the SoundPort CLI
    If this is your first time using this app please reference the README 
    in order to know how to obtain your Spotify API authentication. You will be redirected to a webpage after to authenticate with Spotify.
    Copy and paste the URL you are redirected to in the terminal.

    Otherwise, here are the commands you can use:
    get_playlists: Get all playlists of the current user
    get_tracks:    Get tracks of a playlist
    exit:
    """)
    


    playlist_URIs, tracks = setup_app(setup_auth())

    value = click.prompt('What would you like to do: ', type=click.Choice(list(cli.commands.keys()) + ['exit']))
    click.echo('\n')
    
    while value != 'exit':  
        cli.commands[value]()
    
        if value == 'get-playlists':
            get_playlists(playlist_URIs)
            
        elif value == 'get-tracks':
            get_tracks(tracks)
            
        
# def main():    
#     while True:
#         try:
#            cli.main(standalone_mode=False)
#         except click.exceptions.Abort:
#            break 

if __name__ == '__main__':
    main()
