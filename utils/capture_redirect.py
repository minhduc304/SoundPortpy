import http.server
import socketserver
import threading
import threading
from urllib.parse import urlparse, parse_qs


class OAuthHandler(http.server.BaseHTTPRequestHandler):
    auth_code = None

    def do_GET(self):
        """Handle the OAuth redirect request."""
        query_params = parse_qs(urlparse(self.path).query)
        if "code" in query_params:
            OAuthHandler.auth_code = query_params["code"][0]
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Authentication successful. You can close this window.")

    def log_message(self, format, *args):
        return  # Suppress logging output

def start_local_server(port=8080):
    """Start a temporary local HTTP server to catch OAuth redirects."""
    server = socketserver.TCPServer(("127.0.0.1", port), OAuthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server