import http.server
import socketserver
import threading
import webbrowser
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from urllib.parse import urlparse, parse_qs

class SpotifyAuthHandler(http.server.SimpleHTTPRequestHandler):
    auth_code = None
    
    def do_GET(self):
        # Parse the query parameters
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        
        # Check if the path contains the authorization code
        if 'code' in query_params:
            SpotifyAuthHandler.auth_code = query_params['code'][0]
            
            # Send a response back to the user
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Authentication successful! You can close this window.')
        
        return

def start_local_server(port=8000):
    """Start a local server to capture the Spotify redirect"""
    handler = SpotifyAuthHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving at port {port}")
        httpd.serve_forever()

def get_spotify_auth_code(client_id, client_secret, redirect_uri, scope):
    """
    Automatically obtain Spotify authorization code by starting a local server
    and opening the Spotify authorization URL in the default web browser
    """
    # Create the SpotifyOAuth object
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope
    )
    
    # Start the local server in a separate thread
    server_thread = threading.Thread(target=start_local_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Get the authorization URL
    auth_url = auth_manager.get_authorize_url()
    
    # Open the authorization URL in the default web browser
    webbrowser.open(auth_url)
    
    # Wait until the auth code is captured
    while SpotifyAuthHandler.auth_code is None:
        pass
    
    # Get the access token using the captured authorization code
    token_info = auth_manager.get_access_token(SpotifyAuthHandler.auth_code)
    
    return token_info

def setup_auth():
    """Modified authentication setup to use the new automatic auth method"""
    scope = "playlist-read-private"
    
    # Load environment variables (ensure you have python-dotenv installed)
    from dotenv import load_dotenv
    load_dotenv()
    
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
    
    # Get token info automatically
    token_info = get_spotify_auth_code(client_id, client_secret, redirect_uri, scope)
    
    # Create Spotify client with the obtained token
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope
    )
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    # Get current user
    current_user = sp.me()['uri'].split(":")[-1]
    
    return [sp, current_user]