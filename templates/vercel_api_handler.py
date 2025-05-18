"""
Vercel API Handler for Switch applications

This module provides a handler for running Switch applications on Vercel.
It handles:
1. Routing requests to the appropriate handler
2. Rendering Switch components
3. Serving static files
"""

import os
import sys
import json
import importlib.util
import re
from http.server import BaseHTTPRequestHandler
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Import the Mono Switch framework
try:
    from lib.mono_switch import SwitchComponent, SwitchRenderer
    from lib.mono_http import Request, Response, HttpStatus
    from lib.switch_interpreter import SwitchInterpreter
    from lib.mono_switch_app import SwitchApp, get_switch_app, set_switch_app

    # Check if we have the main application module
    main_module = None
    main_file_path = None

    # Look for the main Mono file
    for file in os.listdir(Path(__file__).resolve().parent.parent.parent):
        if file.endswith(".mono") and "main" in file.lower():
            main_file_path = os.path.join(Path(__file__).resolve().parent.parent.parent, file)
            break

    # Create an interpreter
    interpreter = SwitchInterpreter(use_ssr=True, use_hmr=False, use_kits=True, debug=False)

    # Create a Switch application
    app = SwitchApp(use_ssr=True, use_hmr=False, debug=False)
    set_switch_app(app)

    # Run the main file if found
    if main_file_path:
        interpreter.run_file(main_file_path)

    # Flag to indicate that the framework is loaded
    FRAMEWORK_LOADED = True
except ImportError:
    # If the framework is not found, create a minimal implementation
    FRAMEWORK_LOADED = False

    class SwitchComponent:
        def __init__(self, name, props=None, children=None):
            self.name = name
            self.props = props or {}
            self.children = children or []

        def to_json(self):
            return json.dumps({
                "name": self.name,
                "props": self.props
            })

    class SwitchRenderer:
        def __init__(self, title="Switch App", scripts=None, styles=None):
            self.title = title
            self.scripts = scripts or []
            self.styles = styles or []

        def render(self, component):
            return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.5;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
        }}
        .container {{
            background-color: #fff;
            border-radius: 0.5rem;
            box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.1);
            padding: 2rem;
            margin-top: 2rem;
        }}
        .title {{
            margin-top: 0;
        }}
        .message {{
            font-size: 1.25rem;
            margin-bottom: 1.5rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1 class="title">{component.name}</h1>
        <div class="message">This is a placeholder for the {component.name} component.</div>
        <p>The Mono Switch framework could not be loaded. Please make sure it is properly installed.</p>
    </div>
</body>
</html>'''

    class HttpStatus:
        OK = 200
        NOT_FOUND = 404
        INTERNAL_SERVER_ERROR = 500

    class Request:
        def __init__(self, method, path, headers, body=None):
            self.method = method
            self.path = path
            self.headers = headers
            self.body = body

    class Response:
        def __init__(self):
            self.status_code = HttpStatus.OK
            self.headers = {}
            self.body = ""

        def status(self, status_code):
            self.status_code = status_code
            return self

        def header(self, name, value):
            self.headers[name] = value
            return self

        def text(self, body):
            self.body = body
            return self

        def html(self, body):
            self.header("Content-Type", "text/html")
            self.body = body
            return self

        def json(self, data):
            self.header("Content-Type", "application/json")
            self.body = json.dumps(data)
            return self

def handler(event, context):
    """Handle a request from Vercel."""
    # Extract request information
    method = event.get("method", "GET")
    path = event.get("path", "/")
    headers = event.get("headers", {})
    body = event.get("body", "")

    # Create a request object
    request = Request(method, path, headers, body)

    # Create a response object
    response = Response()

    # Handle the request
    if FRAMEWORK_LOADED:
        try:
            # Check if this is a static file request
            if path.startswith("/static/"):
                # Extract the file path
                match = re.match(r"/static/(.*)", path)
                if match:
                    file_path = match.group(1)
                    static_dir = os.path.join(Path(__file__).resolve().parent.parent, "public", "static")
                    full_path = os.path.join(static_dir, file_path)

                    # Check if the file exists
                    if os.path.isfile(full_path):
                        # Determine the content type
                        content_type = "application/octet-stream"
                        if file_path.endswith(".css"):
                            content_type = "text/css"
                        elif file_path.endswith(".js"):
                            content_type = "application/javascript"
                        elif file_path.endswith(".html"):
                            content_type = "text/html"
                        elif file_path.endswith(".json"):
                            content_type = "application/json"
                        elif file_path.endswith(".png"):
                            content_type = "image/png"
                        elif file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
                            content_type = "image/jpeg"
                        elif file_path.endswith(".gif"):
                            content_type = "image/gif"
                        elif file_path.endswith(".svg"):
                            content_type = "image/svg+xml"

                        # Read the file
                        with open(full_path, "rb") as f:
                            content = f.read()

                        # Return the file
                        return {
                            "statusCode": 200,
                            "headers": {
                                "Content-Type": content_type
                            },
                            "body": content,
                            "isBase64Encoded": True
                        }

            # Use the application to handle the request
            if app:
                # If we have an application, use it to handle the request
                if method == "GET" and path == "/":
                    # Render the application
                    html = app.render()

                    # Return the HTML
                    return {
                        "statusCode": 200,
                        "headers": {
                            "Content-Type": "text/html"
                        },
                        "body": html
                    }
                else:
                    # Use the interpreter to handle the request
                    interpreter.http_server.handle_request(request, response)

                    # Return the response
                    return {
                        "statusCode": response.status_code,
                        "headers": response.headers,
                        "body": response.body
                    }
            else:
                # If we don't have an application, use the interpreter directly
                interpreter.http_server.handle_request(request, response)

                # Return the response
                return {
                    "statusCode": response.status_code,
                    "headers": response.headers,
                    "body": response.body
                }
        except Exception as e:
            # Return an error
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "text/html"
                },
                "body": f"<h1>500 Internal Server Error</h1><p>{str(e)}</p>"
            }
    else:
        # If the framework is not loaded, show a placeholder
        component = SwitchComponent("Switch App", {"title": "Switch App"})
        renderer = SwitchRenderer("Switch App")
        html = renderer.render(component)

        # Return the HTML
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/html"
            },
            "body": html
        }
