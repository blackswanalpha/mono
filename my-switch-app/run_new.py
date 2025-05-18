#!/usr/bin/env python3
"""
Run Switch Application - Simple script to run a Switch application
"""

import os
import sys
import subprocess
import time

def main():
    """Run the Switch application."""
    # Get the file to run
    file_path = "main.mono"

    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return 1
        
    # Define the port
    PORT = 8888

    # Start the HTTP server
    server_code = f'''
import os
import sys
import http.server
import socketserver
import threading
import json

# Set up the HTTP server
PORT = {PORT}

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
        return super().translate_path(path)

    def do_GET(self):
        # Serve static files and Mono files directly
        if self.path.startswith('/static/') or self.path.startswith('/src/'):
            return super().do_GET()

        # Serve the index.html file
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Create the HTML content
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>my-switch-app</title>

    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">

    <!-- Switch Framework Styles -->
    <link rel="stylesheet" href="/static/css/switch.css">
    <link rel="stylesheet" href="/static/css/ui.css">
    <link rel="stylesheet" href="/static/css/app.css">

    <!-- Initial Component Data -->
    <script>
        window.SWITCH_INITIAL_DATA = {
            name: "App",
            props: {
                title: "my-switch-app",
                currentPage: "home"
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
    <div id="switch-root">
        <!-- Server-rendered content will be placed here -->
        <div id="server-rendered-content">
            <!-- This will be populated with the server-rendered HTML -->
        </div>
    </div>
    
    <!-- Mono Root Element -->
    <div id="mono-root" style="display: none;">
        <!-- Mono components will be rendered here -->
    </div>
    
    <!-- Mono Display Controls -->
    <div id="mono-controls" style="position: fixed; bottom: 20px; right: 20px; z-index: 1000; background-color: rgba(255, 255, 255, 0.9); padding: 15px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
        <h4 style="margin-top: 0; margin-bottom: 10px; font-size: 16px; color: #333;">Mono Display</h4>
        <button id="display-home-mono" class="btn btn-primary" style="margin-right: 10px; padding: 8px 16px; font-weight: bold;">Display home.mono</button>
        <button id="display-fallback-home-mono" class="btn btn-secondary" style="padding: 8px 16px; font-weight: bold;">Display fallback-home.mono</button>
    </div>
    
    <!-- Mono Display Script -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            /* Add event listeners to the buttons */
            document.getElementById('display-home-mono').addEventListener('click', function() {
                if (window.MonoDisplay) {
                    window.MonoDisplay.displayMonoFile('/src/pages/home.mono');
                }
            });
            
            document.getElementById('display-fallback-home-mono').addEventListener('click', function() {
                if (window.MonoDisplay) {
                    window.MonoDisplay.displayMonoFile('/src/pages/fallback-home.mono');
                }
            });
        });
    </script>

    <!-- Switch Framework Scripts -->
    <script src="/static/js/dom.js"></script>
    <script src="/static/js/switch.js"></script>
    <script src="/static/js/store.js"></script>
    <script src="/static/js/components.js"></script>
    <script src="/static/js/ssr.js"></script>
    <script src="/static/js/ui.js"></script>
    <script src="/static/js/app.js"></script>
    <script src="/static/js/index.js"></script>

    <!-- Initialize Component -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            /* Create a simple Switch object if it doesn't exist */
            if (!window.Switch) {
                window.Switch = {
                    /* Store components */
                    components: {},

                    /* Create a component */
                    createComponent: function(data) {
                        console.log('Creating component:', data);
                        const component = {
                            id: 'app-' + Date.now(),
                            name: data.name,
                            props: data.props || {},
                            state: {
                                title: data.props.title || "my-switch-app",
                                currentPage: data.props.currentPage || "home",
                                darkMode: false,
                                sidebarCollapsed: false
                            },
                            render: function() {
                                /* Use the server-rendered HTML if available */
                                const serverRendered = document.getElementById('server-rendered-content');
                                if (serverRendered) {
                                    console.log('Using server-rendered content');
                                    /* Make the server-rendered content visible */
                                    serverRendered.style.display = 'block';
                                    return serverRendered.innerHTML;
                                }

                                console.log('No server-rendered content found, using fallback');
                                /* Fallback to client-side rendering */
                                return '<div class="app"><h1>' + this.props.title + '</h1><p>Welcome to Switch!</p></div>';
                            }
                        };

                        /* Store the component */
                        this.components[component.id] = component;

                        return component;
                    },

                    /* Register a component */
                    component: function(name, props) {
                        return { name, props };
                    },

                    /* Render a component */
                    renderComponent: function(component, container) {
                        console.log('Rendering component:', component);
                        if (container) {
                            /* Use the component's render method */
                            const html = component.render();

                            /* Update the container */
                            container.innerHTML = html;

                            /* Add event listeners */
                            this.addEventListeners(container);
                        }
                    },

                    /* Add event listeners to elements with data-event attributes */
                    addEventListeners: function(container) {
                        /* Find all elements with data-event attributes */
                        const elements = container.querySelectorAll('[data-event]');

                        /* Add event listeners */
                        elements.forEach(element => {
                            const eventType = element.dataset.event;
                            const action = element.dataset.action;

                            /* Add the event listener */
                            element.addEventListener(eventType, event => {
                                /* Handle the event */
                                this.handleEvent(event, action);
                            });
                        });
                    },

                    /* Handle an event */
                    handleEvent: function(event, action) {
                        /* Get the target element */
                        const target = event.target;

                        /* Handle navigation */
                        if (action === 'navigate') {
                            /* Prevent the default link behavior */
                            event.preventDefault();

                            /* Get the page */
                            const page = target.dataset.page;

                            /* Update the URL */
                            if (page === 'home') {
                                history.pushState({}, '', '/');
                            } else {
                                history.pushState({}, '', '/' + page);
                            }

                            /* Reload the page */
                            window.location.reload();
                        }

                        /* Handle dark mode toggle */
                        if (action === 'toggle-dark-mode') {
                            /* Toggle the dark mode class on the body */
                            document.body.classList.toggle('dark-mode');

                            /* Store the preference */
                            localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
                        }

                        /* Handle sidebar toggle */
                        if (action === 'toggle-sidebar') {
                            /* Toggle the sidebar-collapsed class on the body */
                            document.body.classList.toggle('sidebar-collapsed');

                            /* Store the preference */
                            localStorage.setItem('sidebarCollapsed', document.body.classList.contains('sidebar-collapsed'));
                        }
                    },

                    /* Initialize the framework */
                    init: function(options) {
                        console.log('Switch framework initialized with options:', options);

                        /* Apply user preferences */
                        this.applyUserPreferences();
                    },

                    /* Apply user preferences */
                    applyUserPreferences: function() {
                        /* Apply dark mode preference */
                        if (localStorage.getItem('darkMode') === 'true') {
                            document.body.classList.add('dark-mode');
                        }

                        /* Apply sidebar preference */
                        if (localStorage.getItem('sidebarCollapsed') === 'true') {
                            document.body.classList.add('sidebar-collapsed');
                        }
                    },

                    /* Check if running in the browser */
                    isClient: function() {
                        return true;
                    },

                    /* Client-side event registration */
                    clientEvent: function(eventType, handlerName) {
                        /* This is just a stub for the server-side function */
                    }
                };
            }

            /* Create the component */
            const component = Switch.createComponent(window.SWITCH_INITIAL_DATA);

            /* Render the component */
            Switch.renderComponent(component, document.getElementById('switch-root'));

            /* Enable HMR if configured */
            if (window.SWITCH_ENV.hmr && window.Switch.hmr) {
                Switch.hmr.enable({
                    debug: window.SWITCH_ENV.debug
                });
            }
        });
    </script>
</body>
</html>"""

        self.wfile.write(html.encode())

# Create the server
with socketserver.TCPServer(("", PORT), SwitchHandler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()
'''

    # Start the HTTP server
    process = subprocess.Popen([
        "python3",
        "-c",
        server_code
    ])

    # Wait for the server to start
    time.sleep(1)

    # Open the browser
    try:
        import webbrowser
        webbrowser.open(f"http://localhost:{PORT}")
    except:
        print(f"Please open your browser and navigate to http://localhost:{PORT}")

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
