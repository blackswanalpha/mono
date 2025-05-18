#!/usr/bin/env python3
"""
Simple HTTP server for the Switch application
"""

import http.server
import socketserver
import os
import json

# Configuration
PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class SwitchHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for the Switch application."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        # API endpoints
        if self.path.startswith('/api/'):
            self.handle_api()
            return
        
        # For all other paths, serve the index.html file for client-side routing
        if not self.path.startswith('/static/') and not os.path.exists(os.path.join(DIRECTORY, self.path[1:])):
            self.path = '/index.html'
        
        return super().do_GET()
    
    def handle_api(self):
        """Handle API requests."""
        # Packages API
        if self.path == '/api/packages':
            self.send_json({
                'status': 'success',
                'data': [
                    {
                        'name': 'http-client',
                        'version': '1.0.0',
                        'description': 'HTTP client for Switch applications',
                        'author': 'Switch Team',
                        'license': 'MIT',
                        'dependencies': {
                            'switch-core': '^1.0.0'
                        },
                        'installed': True
                    },
                    {
                        'name': 'date-formatter',
                        'version': '1.0.0',
                        'description': 'Date formatting utilities for Switch applications',
                        'author': 'Switch Team',
                        'license': 'MIT',
                        'dependencies': {
                            'switch-core': '^1.0.0'
                        },
                        'installed': True
                    },
                    {
                        'name': 'storage-manager',
                        'version': '1.0.0',
                        'description': 'Storage management utilities for Switch applications',
                        'author': 'Switch Team',
                        'license': 'MIT',
                        'dependencies': {
                            'switch-core': '^1.0.0'
                        },
                        'installed': True
                    },
                    {
                        'name': 'state-manager',
                        'version': '1.0.0',
                        'description': 'State management utilities for Switch applications',
                        'author': 'Switch Team',
                        'license': 'MIT',
                        'dependencies': {
                            'switch-core': '^1.0.0'
                        },
                        'installed': True
                    },
                    {
                        'name': 'router',
                        'version': '1.0.0',
                        'description': 'Routing utilities for Switch applications',
                        'author': 'Switch Team',
                        'license': 'MIT',
                        'dependencies': {
                            'switch-core': '^1.0.0'
                        },
                        'installed': True
                    }
                ]
            })
            return
        
        # Kits API
        if self.path == '/api/kits':
            self.send_json({
                'status': 'success',
                'data': [
                    {
                        'name': 'SwitchUIKit',
                        'version': '1.0.0',
                        'description': 'UI Kit for Switch applications',
                        'author': 'Switch Team',
                        'license': 'MIT',
                        'dependencies': {
                            'switch-core': '^1.0.0'
                        },
                        'components': [
                            'Button', 'Card', 'Alert', 'Modal', 'Tabs', 'Dropdown', 'Form'
                        ],
                        'installed': True
                    },
                    {
                        'name': 'SwitchFormKit',
                        'version': '1.0.0',
                        'description': 'Form components for Switch applications',
                        'author': 'Switch Team',
                        'license': 'MIT',
                        'dependencies': {
                            'switch-core': '^1.0.0',
                            'switch-ui-kit': '^1.0.0'
                        },
                        'components': [
                            'Input', 'Checkbox', 'Radio', 'Select', 'Textarea', 'DatePicker', 'TimePicker'
                        ],
                        'installed': True
                    },
                    {
                        'name': 'SwitchDataKit',
                        'version': '1.0.0',
                        'description': 'Data visualization components for Switch applications',
                        'author': 'Switch Team',
                        'license': 'MIT',
                        'dependencies': {
                            'switch-core': '^1.0.0',
                            'switch-ui-kit': '^1.0.0'
                        },
                        'components': [
                            'Table', 'Chart', 'Graph', 'Map', 'Timeline', 'Calendar', 'Dashboard'
                        ],
                        'installed': True
                    }
                ]
            })
            return
        
        # Default response for unknown API endpoints
        self.send_json({
            'status': 'error',
            'message': 'API endpoint not found'
        }, status=404)
    
    def send_json(self, data, status=200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

def main():
    """Main entry point."""
    # Create server
    handler = SwitchHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    
    print(f"Starting server at http://localhost:{PORT}")
    
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
