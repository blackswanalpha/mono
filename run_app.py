#!/usr/bin/env python3
"""
Run a Switch application
"""

import os
import sys
import http.server
import socketserver
import json
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Default port
PORT = 8080

class SwitchHandler(http.server.SimpleHTTPRequestHandler):
    """Handler for Switch applications."""

    def do_GET(self):
        """Handle GET requests."""
        # Serve static files
        if self.path.startswith('/static/'):
            # Remove the leading slash
            file_path = self.path[1:]

            # Check if the file exists
            if os.path.isfile(file_path):
                # Determine content type
                content_type = self._get_content_type(file_path)

                # Send response
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()

                # Send file content
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())

                return

        # Serve app.css
        if self.path == '/app.css':
            # Check if the file exists
            if os.path.isfile('app.css'):
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'text/css')
                self.end_headers()

                # Send file content
                with open('app.css', 'rb') as f:
                    self.wfile.write(f.read())

                return

        # Serve index.html for all other paths
        if os.path.isfile('index.html'):
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # Send file content
            with open('index.html', 'rb') as f:
                self.wfile.write(f.read())

            return

        # File not found
        self.send_response(404)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'File not found')

    def _get_content_type(self, file_path):
        """Get content type based on file extension."""
        # Get file extension
        _, ext = os.path.splitext(file_path)

        # Determine content type
        if ext == '.css':
            return 'text/css'
        elif ext == '.js':
            return 'application/javascript'
        elif ext == '.html':
            return 'text/html'
        elif ext == '.png':
            return 'image/png'
        elif ext == '.jpg' or ext == '.jpeg':
            return 'image/jpeg'
        elif ext == '.gif':
            return 'image/gif'
        elif ext == '.svg':
            return 'image/svg+xml'
        else:
            return 'application/octet-stream'

def main():
    """Main entry point."""
    # Get port from environment variable
    port = int(os.environ.get('PORT', PORT))

    # Create server
    handler = SwitchHandler
    httpd = socketserver.TCPServer(("", port), handler)

    print(f"Starting server at http://localhost:{port}")

    try:
        # Start server
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped")
    finally:
        # Close server
        httpd.server_close()

if __name__ == "__main__":
    main()
