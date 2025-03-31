import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
from collections import defaultdict
import click
from tqdm import tqdm
from utils.capture_redirect import get_spotify_auth_code
import time


def setup_auth():
    """
    Authentication setup to capture redirect URL and get token info.
    Sets up the Spotify client with the user's credentials.

    Returns:
        list: A list containing the Spotify client and the current user's ID.
    """

    # Load environment variables
    scope = "playlist-read-private"
    from dotenv import load_dotenv

    load_dotenv()

    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

    # # Get token info automatically
    # token_info = get_spotify_auth_code(client_id, client_secret, redirect_uri, scope)

    # if token_info is None:
    #     raise Exception("Authentication failed")

    # Create Spotify client with the obtained token
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
    )

    sp = spotipy.Spotify(auth_manager=auth_manager)

    # Get current user
    current_user = sp.me()["uri"].split(":")[-1]

    return [sp, current_user]


def setup_app(auth):
    """
    Sets up the application by retrieving the user's playlists and tracks.

    Args:
        auth (list): A list containing the Spotify client and the current user's ID.

    Returns:
        list: A list containing the playlist URIs and the tracks.
    """
    # Get the user's playlists
    sp = auth[0]
    current_user = auth[1]
    playlist_URIs = []
    playlists = sp.user_playlists(user=current_user)
    while playlists:
        for playlist in playlists["items"]:
            # print(f"{i + 1 + playlists['offset']:4d} {playlist['uri']} {playlist['name']}")
            playlist_URIs.append(playlist["uri"].split(":")[2] + ":" + playlist["name"])
        if playlists["next"]:
            playlists = sp.next(playlists)
        else:
            playlists = None

    tracks = defaultdict(list)

    for uri in tqdm(playlist_URIs):
        try:
            for track in sp.playlist_tracks(uri.split(":")[0])["items"]:
                tracks[uri.split(":")[-1]].append(track["track"]["name"])
        except Exception as e:
            print(f"Error getting tracks for playlist {uri}: {e}")

    return [playlist_URIs, tracks]


@click.group()
def cli():
    """
    Defines the command-line interface for the application.
    """
    pass


@cli.command()
def get_playlists():
    """
    Get the playlists of the current user.
    """
    click.echo("Here are your playlists:")
    # Access playlist_URIs from the main function's scope
    try:
        for playlist in globals()['playlist_URIs']:
            click.echo(playlist.split(":")[-1])
    except NameError:
        click.echo("Error: playlist_URIs not found. Please run the app first.")



@cli.command()
@click.option(
    "--name",
    prompt="Enter the name of the playlist you want to see the tracks of",
    help="The name of the playlist",
)
def get_tracks(name, tracks):
    """
    Get the tracks of a playlist.
    Make sure to copy and paste the URL that you were redirected to after running the app.
    """
    click.echo(f"Tracks from {name}:")
    for track in tracks[name]:
        click.echo(track)


def main():
    """
    Main function of the application.
    """

    click.echo(
        """
                                                                                                                        
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
    """
    )

    # time.sleep(5)
    # Setup authentication and app
    input_list = setup_app(setup_auth())
    playlist_URIs = input_list[0]
    tracks = input_list[1]

    valid_choices = list(cli.commands.keys()) + ["exit"]
    value = click.prompt(
        "What would you like to do: ", type=click.Choice(valid_choices)
    )
    click.echo("\n")

    while value != "exit":
        if value == "get-playlists":
            get_playlists()
        elif value == "get-tracks":
            get_tracks(name=value, tracks=tracks)
        value = click.prompt(
            "What would you like to do: ", type=click.Choice(valid_choices)
        )
        click.echo("\n")


if __name__ == "__main__":
    main()
