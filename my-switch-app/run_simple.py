#!/usr/bin/env python3
"""
Run Switch Application - Simple script to run a Switch application
"""

import os
import sys
import http.server
import socketserver
import webbrowser

# Define the port
PORT = 8888

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
        return super().translate_path(path)

def main():
    """Run the Switch application."""
    # Check if the main file exists
    if not os.path.exists('main.mono'):
        print("Error: File not found: main.mono")
        return 1
        
    # Check if the index.html file exists
    if not os.path.exists('index.html'):
        print("Error: File not found: index.html")
        return 1

    # Create the server
    with socketserver.TCPServer(("", PORT), SwitchHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        
        # Open the browser
        try:
            webbrowser.open(f"http://localhost:{PORT}")
        except:
            print(f"Please open your browser and navigate to http://localhost:{PORT}")
            
        # Start the server
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nApplication stopped")
            return 0

if __name__ == "__main__":
    sys.exit(main())
