#!/usr/bin/env python3
"""
Run Switch Introduction - Simple script to run the Switch introduction application
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def main():
    """Run the Switch introduction application."""
    # Get the file to run
    file_path = "simple.mono"

    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return 1

    # Start the HTTP server
    process = subprocess.Popen([
        "python3",
        "-c",
        """
import os
import sys
import http.server
import socketserver
import threading
import json

# Set up the HTTP server
PORT = 9999

# Create a custom handler that serves our app
class SwitchHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Map /static/ to static/
        if path.startswith('/static/'):
            return os.path.join(os.getcwd(), path[1:])
        return super().translate_path(path)

    def do_GET(self):
        # Serve the main page for all routes except static files
        if self.path.startswith('/static/'):
            return super().do_GET()

        # Serve the index.html file
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Create the HTML content
        html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Introduction to Switch</title>

    <!-- Switch Framework Styles -->
    <link rel="stylesheet" href="/static/css/app.css">

    <!-- Initial Component Data -->
    <script>
        window.SWITCH_INITIAL_DATA = {
            name: "App",
            props: {
                title: "Introduction to Switch",
                message: "Welcome to the Switch framework!"
            }
        };

        window.SWITCH_ENV = {
            debug: true,
            hmr: true,
            ssr: false
        };
    </script>
</head>
<body>
    <!-- Root Element -->
    <div id="switch-root"></div>

    <!-- Switch Framework Scripts -->
    <script src="/static/js/app.js"></script>

    <!-- Initialize Component -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Create the component
            const component = Switch.createComponent(window.SWITCH_INITIAL_DATA);

            // Render the component
            Switch.renderComponent(component, document.getElementById('switch-root'));
        });
    </script>
</body>
</html>'''

        self.wfile.write(html.encode())

# Create the server
with socketserver.TCPServer(("", PORT), SwitchHandler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()
        """
    ])

    # Wait for the server to start
    time.sleep(1)

    # Open the browser
    try:
        import webbrowser
        webbrowser.open(f"http://localhost:9999")
    except:
        print("Please open your browser and navigate to http://localhost:9999")

    # Wait for the server to finish
    try:
        process.wait()
        return 0
    except KeyboardInterrupt:
        # Stop the server
        process.terminate()
        print("\nApplication stopped")
        return 0

if __name__ == "__main__":
    sys.exit(main())
