#!/usr/bin/env python3
"""
Run Switch Application - Enhanced script to run a Switch application with dynamic features
"""

import os
import sys
import subprocess
import time
import webbrowser
import argparse
import json

def main():
    """Run the Switch application with enhanced features."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run a Switch application with enhanced features")
    parser.add_argument("--port", type=int, default=5555, help="Port to run the server on (default: 5555)")
    parser.add_argument("--host", default="localhost", help="Host to run the server on (default: localhost)")
    parser.add_argument("--reload", action="store_true", help="Enable live reloading")
    parser.add_argument("--hmr", action="store_true", help="Enable hot module replacement")
    parser.add_argument("--ssr", action="store_true", help="Enable server-side rendering")
    parser.add_argument("--hydrate", action="store_true", help="Enable hydration")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--open", action="store_true", default=True, help="Open browser automatically")
    args = parser.parse_args()

    # Get the file to run
    file_path = "main.mono"

    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return 1

    # Check if the index.html file exists
    if not os.path.exists('index.html'):
        print("Error: File not found: index.html")
        return 1

    # Define the port
    PORT = args.port
    HOST = args.host
    DEBUG = args.debug
    RELOAD = args.reload
    HMR = args.hmr
    SSR = args.ssr
    HYDRATE = args.hydrate

    # Create the settings object
    settings = {
        "port": PORT,
        "host": HOST,
        "debug": DEBUG,
        "reload": RELOAD,
        "hmr": HMR,
        "ssr": SSR,
        "hydrate": HYDRATE,
        "appName": os.path.basename(os.getcwd()),
        "rootDir": os.getcwd(),
        "srcDir": os.path.join(os.getcwd(), "src"),
        "componentsDir": os.path.join(os.getcwd(), "src", "components"),
        "pagesDir": os.path.join(os.getcwd(), "src", "pages"),
        "staticDir": os.path.join(os.getcwd(), "src", "static"),
        "layoutsDir": os.path.join(os.getcwd(), "src", "layouts"),
        "framesDir": os.path.join(os.getcwd(), "src", "frames")
    }

    # Create the settings directory if it doesn't exist
    settings_dir = os.path.join(os.getcwd(), ".switch", "settings")
    os.makedirs(settings_dir, exist_ok=True)

    # Write the settings to a file
    with open(os.path.join(settings_dir, "app.json"), "w") as f:
        json.dump(settings, f, indent=2)

    # Start the HTTP server
    process = subprocess.Popen([
        "python3",
        "-c",
        '''
import os
import sys
import http.server
import socketserver
import threading
import json
import re
import time
import signal
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Set up the HTTP server
PORT = """ + str(PORT) + """
HOST = """ + f'"{HOST}"' + """
DEBUG = """ + str(DEBUG).lower() + """
RELOAD = """ + str(RELOAD).lower() + """
HMR = """ + str(HMR).lower() + """
SSR = """ + str(SSR).lower() + """
HYDRATE = """ + str(HYDRATE).lower() + """

# Load settings
SETTINGS_PATH = os.path.join(os.getcwd(), ".switch", "settings", "app.json")
with open(SETTINGS_PATH, "r") as f:
    SETTINGS = json.load(f)

# Component cache
COMPONENT_CACHE = {{}}
FRAME_CACHE = {{}}
LAYOUT_CACHE = {{}}

# File watchers
FILE_WATCHERS = {{}}
LAST_MODIFIED = {{}}

# Create a custom handler that serves our app
class SwitchHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        if DEBUG:
            super().log_message(format, *args)

    def translate_path(self, path):
        # Parse the URL to get query parameters
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # Map /static/ to src/static/
        if path.startswith('/static/'):
            return os.path.join(os.getcwd(), 'src' + path)
        # Map /src/ paths directly to the file system
        elif path.startswith('/src/'):
            return os.path.join(os.getcwd(), path[1:])  # Remove the leading slash
        # Map /lib/ paths directly to the file system
        elif path.startswith('/lib/'):
            return os.path.join(os.getcwd(), 'src' + path)
        # Map /app.css to the root app.css file (for backward compatibility)
        elif path == '/app.css':
            return os.path.join(os.getcwd(), 'app.css')
        # Map /switch-api/ to API endpoints
        elif path.startswith('/switch-api/'):
            return path  # Special handling in do_GET
        # Map / to index.html
        elif path == '/':
            return os.path.join(os.getcwd(), 'index.html')
        # Default translation
        return super().translate_path(path)

    def do_GET(self):
        # Parse the URL to get query parameters
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)

        # Handle API endpoints
        if path.startswith('/switch-api/'):
            self.handle_api_request(path, query)
            return

        # Handle component requests
        if path.endswith('.mono'):
            self.serve_mono_component(path)
            return

        # Handle SSR requests
        if SSR and path == '/':
            self.serve_ssr_page(path, query)
            return

        # Default handling
        return super().do_GET()

    def serve_ssr_page(self, path, query):
        """Serve a server-side rendered page."""
        try:
            # Get the index.html file
            with open(os.path.join(os.getcwd(), 'index.html'), 'r') as f:
                html = f.read()

            # Get the initial component data
            initial_data = self.get_initial_data()

            # Render the components on the server
            rendered_html = self.render_components(initial_data)

            # Insert the rendered HTML into the page
            html = html.replace('<div id="app-container" class="fade-in">',
                               '<div id="app-container" class="fade-in">' + rendered_html)

            # Add hydration data if enabled
            if HYDRATE:
                # Update the initial data to include hydration flag
                initial_data['hydrate'] = True

                # Update the SWITCH_INITIAL_DATA in the HTML
                html = html.replace('window.SWITCH_INITIAL_DATA = {',
                                   'window.SWITCH_INITIAL_DATA = ' + json.dumps(initial_data))

            # Send the response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        except Exception as e:
            print(f"Error serving SSR page: {e}")
            # Fall back to regular page
            return super().do_GET()

    def get_initial_data(self):
        """Get the initial component data for SSR."""
        # This would typically come from a database or API
        # For now, we'll use a simple example
        return {
            "name": "App",
            "props": {
                "title": SETTINGS["appName"],
                "currentPage": "home"
            },
            "components": [
                {
                    "id": "layout-component",
                    "name": "Layout",
                    "props": {
                        "title": SETTINGS["appName"],
                        "currentPage": "home"
                    }
                }
            ],
            "frames": [
                {
                    "id": "main-frame",
                    "name": "MainFrame",
                    "state": {
                        "title": "Server Rendered Frame",
                        "theme": "light"
                    }
                }
            ]
        }

    def render_components(self, data):
        """Render components on the server."""
        # In a real implementation, this would use a server-side renderer
        # For now, we'll return a simple placeholder
        return """
            <div class="server-rendered">
                <div class="ssr-notice">
                    <strong>Server-Side Rendered Content</strong>
                    <p>This content was rendered on the server.</p>
                </div>
                <div data-component="Layout" data-component-id="' + data['components'][0]['id'] + '">
                    <div class="app">
                        <div class="app-header">
                            <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
                                <div class="container">
                                    <a class="navbar-brand" href="/" data-nav="true">
                                        <img src="src/static/img/switch-logo.svg" alt="Switch Logo" width="30" height="30" class="d-inline-block align-top me-2">
                                        ' + data['props']['title'] + '
                                    </a>
                                </div>
                            </nav>
                        </div>
                        <div class="app-container">
                            <div class="app-content">
                                <div class="content-container">
                                    <div data-frame="MainFrame" data-frame-id="' + data['frames'][0]['id'] + '">
                                        <div class="main-frame">
                                            <div class="frame-header">
                                                <h1>' + data['frames'][0]['state']['title'] + '</h1>
                                                <button class="theme-toggle" data-event="click" data-action="toggleTheme">
                                                    <i class="bi bi-moon"></i>
                                                </button>
                                            </div>
                                            <div class="frame-content">
                                                <div data-frame-children></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        """

    def handle_api_request(self, path, query):
        """Handle API requests."""
        endpoint = path.replace('/switch-api/', '')

        if endpoint == 'components':
            # List all components
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            components_dir = SETTINGS['componentsDir']
            components = []

            for root, dirs, files in os.walk(components_dir):
                for file in files:
                    if file.endswith('.mono'):
                        rel_path = os.path.relpath(os.path.join(root, file), os.getcwd())
                        components.append({
                            'path': rel_path,
                            'name': os.path.splitext(file)[0],
                            'type': 'component'
                        })

            self.wfile.write(json.dumps(components).encode())

        elif endpoint == 'pages':
            # List all pages
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            pages_dir = SETTINGS['pagesDir']
            pages = []

            for root, dirs, files in os.walk(pages_dir):
                for file in files:
                    if file.endswith('.mono'):
                        rel_path = os.path.relpath(os.path.join(root, file), os.getcwd())
                        pages.append({
                            'path': rel_path,
                            'name': os.path.splitext(file)[0],
                            'type': 'page'
                        })

            self.wfile.write(json.dumps(pages).encode())

        elif endpoint == 'layouts':
            # List all layouts
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            layouts_dir = SETTINGS['layoutsDir']
            layouts = []

            if os.path.exists(layouts_dir):
                for root, dirs, files in os.walk(layouts_dir):
                    for file in files:
                        if file.endswith('.mono'):
                            rel_path = os.path.relpath(os.path.join(root, file), os.getcwd())
                            layouts.append({
                                'path': rel_path,
                                'name': os.path.splitext(file)[0],
                                'type': 'layout'
                            })

            self.wfile.write(json.dumps(layouts).encode())

        elif endpoint == 'frames':
            # List all frames
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            frames_dir = SETTINGS['framesDir']
            frames = []

            if os.path.exists(frames_dir):
                for root, dirs, files in os.walk(frames_dir):
                    for file in files:
                        if file.endswith('.mono'):
                            rel_path = os.path.relpath(os.path.join(root, file), os.getcwd())
                            frames.append({
                                'path': rel_path,
                                'name': os.path.splitext(file)[0],
                                'type': 'frame'
                            })

            self.wfile.write(json.dumps(frames).encode())

        elif endpoint == 'hmr':
            # Handle HMR requests
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Check if any files have changed
            changes = []

            for file_path, last_modified in LAST_MODIFIED.items():
                try:
                    current_mtime = os.path.getmtime(file_path)
                    if current_mtime > last_modified:
                        LAST_MODIFIED[file_path] = current_mtime
                        changes.append({
                            'path': os.path.relpath(file_path, os.getcwd()),
                            'type': 'modified'
                        })
                except FileNotFoundError:
                    # File was deleted
                    changes.append({
                        'path': os.path.relpath(file_path, os.getcwd()),
                        'type': 'deleted'
                    })
                    del LAST_MODIFIED[file_path]

            # Check for new files
            for root, dirs, files in os.walk(SETTINGS['srcDir']):
                for file in files:
                    if file.endswith('.mono'):
                        file_path = os.path.join(root, file)
                        if file_path not in LAST_MODIFIED:
                            LAST_MODIFIED[file_path] = os.path.getmtime(file_path)
                            changes.append({
                                'path': os.path.relpath(file_path, os.getcwd()),
                                'type': 'added'
                            })

            self.wfile.write(json.dumps({
                'changes': changes
            }).encode())

        else:
            # Unknown endpoint
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': f'Unknown endpoint: {endpoint}'
            }).encode())

    def serve_mono_component(self, path):
        """Serve a Mono component."""
        # Get the file path
        file_path = self.translate_path(path)

        # Check if the file exists
        if not os.path.exists(file_path):
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"File not found: {path}".encode())
            return

        # Read the file
        with open(file_path, 'r') as f:
            content = f.read()

        # Parse the component
        component_name = self.parse_component_name(content)

        # Add to component cache
        COMPONENT_CACHE[path] = {
            'name': component_name,
            'content': content,
            'last_modified': os.path.getmtime(file_path)
        }

        # Add to file watchers
        if RELOAD or HMR:
            LAST_MODIFIED[file_path] = os.path.getmtime(file_path)

        # Send the response
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(content.encode())

    def parse_component_name(self, content):
        """Parse the component name from the content."""
        match = re.search(r'component\s+([A-Za-z0-9_]+)', content)
        if match:
            return match.group(1)
        return "UnknownComponent"

# Initialize file watchers
def init_file_watchers():
    """Initialize file watchers for HMR and live reloading."""
    if not (RELOAD or HMR):
        return

    print("Initializing file watchers...")

    # Watch src directory
    for root, dirs, files in os.walk(SETTINGS['srcDir']):
        for file in files:
            if file.endswith('.mono'):
                file_path = os.path.join(root, file)
                LAST_MODIFIED[file_path] = os.path.getmtime(file_path)

    print(f"Watching {len(LAST_MODIFIED)} files for changes")

# Initialize the server
def init_server():
    """Initialize the server."""
    # Initialize file watchers
    init_file_watchers()

    # Create the server
    server = socketserver.TCPServer((HOST, PORT), SwitchHandler)

    print(f"Switch application server running at http://{HOST}:{PORT}")
    print(f"Debug mode: {'enabled' if DEBUG else 'disabled'}")
    print(f"Live reloading: {'enabled' if RELOAD else 'disabled'}")
    print(f"Hot module replacement: {'enabled' if HMR else 'disabled'}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\nServer stopped")
    finally:
        server.server_close()

# Start the server
init_server()
        '''
    ])

    # Wait for the server to start
    time.sleep(1)

    # Open the browser
    if args.open:
        try:
            webbrowser.open(f"http://{HOST}:{PORT}")
            print(f"Opening browser at http://{HOST}:{PORT}")
        except:
            print(f"Please open your browser and navigate to http://{HOST}:{PORT}")

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
