#!/usr/bin/env python3
"""
Simple HTTP server for Switch application
"""

import os
import sys
import http.server
import socketserver
import webbrowser

# Define the port
PORT = 5555

# Create a custom handler that serves our app
class SwitchHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Map /static/ to src/static/
        if path.startswith('/static/'):
            return os.path.join(os.getcwd(), 'src' + path)
        # Map /src/ paths directly to the file system
        elif path.startswith('/src/'):
            return os.path.join(os.getcwd(), path[1:])  # Remove the leading slash
        # Map /app.css to the root app.css file (for backward compatibility)
        elif path == '/app.css':
            return os.path.join(os.getcwd(), 'app.css')
        # Map / to index.html
        elif path == '/':
            return os.path.join(os.getcwd(), 'index.html')
        # Map routes to index.html
        elif path in ['/about', '/tutorials', '/feedback', '/enhanced', '/advanced']:
            return os.path.join(os.getcwd(), 'index.html')
        # Default translation
        return super().translate_path(path)

def main():
    """Run the server."""
    # Create the server
    with socketserver.TCPServer(("", PORT), SwitchHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")

        # Open the browser
        try:
            webbrowser.open(f"http://localhost:{PORT}")
            print(f"Opening browser at http://localhost:{PORT}")
        except:
            print(f"Please open your browser and navigate to http://localhost:{PORT}")

        # Start the server
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")
            return 0

if __name__ == "__main__":
    sys.exit(main())
