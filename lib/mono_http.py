"""
Mono HTTP - HTTP server implementation for the Mono language

This module provides support for:
1. HTTP server: A simple HTTP server for handling web requests
2. Request handling: Parse and handle HTTP requests
3. Response building: Build and send HTTP responses
4. Routing: Route requests to appropriate handlers
"""

import socket
import threading
import json
import re
import traceback
import time
from typing import Dict, List, Any, Optional, Callable, Set, Tuple, Union, TypeVar, Generic
from urllib.parse import parse_qs, urlparse

# Type definitions
Handler = Callable[['Request', 'Response'], None]
Middleware = Callable[['Request', 'Response', Handler], None]

class HttpStatus:
    """HTTP status codes"""
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    SERVICE_UNAVAILABLE = 503

class Request:
    """
    Represents an HTTP request in the Mono language.
    """
    def __init__(self, method: str, path: str, headers: Dict[str, str], body: str, query_params: Dict[str, List[str]]):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body
        self.query_params = query_params
        self.params = {}  # Route parameters

    def get_json(self) -> Any:
        """Parse the request body as JSON."""
        if not self.body:
            return None
        try:
            return json.loads(self.body)
        except json.JSONDecodeError:
            return None

    def get_query_param(self, name: str, default: Any = None) -> Any:
        """Get a query parameter by name."""
        values = self.query_params.get(name, [])
        return values[0] if values else default

    def get_param(self, name: str, default: Any = None) -> Any:
        """Get a route parameter by name."""
        return self.params.get(name, default)

class Response:
    """
    Represents an HTTP response in the Mono language.
    """
    def __init__(self):
        self.status_code = HttpStatus.OK
        self.headers = {
            "Content-Type": "text/plain",
            "Server": "Mono/1.0"
        }
        self.body = ""

    def status(self, code: int) -> 'Response':
        """Set the status code."""
        self.status_code = code
        return self

    def header(self, name: str, value: str) -> 'Response':
        """Set a header."""
        self.headers[name] = value
        return self

    def text(self, content: str) -> 'Response':
        """Set the response body as text."""
        self.body = content
        self.headers["Content-Type"] = "text/plain"
        return self

    def html(self, content: str) -> 'Response':
        """Set the response body as HTML."""
        self.body = content
        self.headers["Content-Type"] = "text/html"
        return self

    def json(self, data: Any) -> 'Response':
        """Set the response body as JSON."""
        self.body = json.dumps(data)
        self.headers["Content-Type"] = "application/json"
        return self

    def to_http_response(self) -> str:
        """Convert the response to an HTTP response string."""
        status_text = {
            200: "OK",
            201: "Created",
            202: "Accepted",
            204: "No Content",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            500: "Internal Server Error",
            501: "Not Implemented",
            503: "Service Unavailable"
        }.get(self.status_code, "Unknown")

        response = f"HTTP/1.1 {self.status_code} {status_text}\r\n"

        # Add headers
        for name, value in self.headers.items():
            response += f"{name}: {value}\r\n"

        # Add Content-Length header
        response += f"Content-Length: {len(self.body)}\r\n"

        # Add body
        response += "\r\n"
        response += self.body

        return response

class Route:
    """
    Represents a route in the Mono HTTP server.
    """
    def __init__(self, method: str, path_pattern: str, handler: Handler):
        self.method = method
        self.path_pattern = path_pattern
        self.handler = handler

        # Convert path pattern to regex
        regex_pattern = "^"
        param_names = []

        # Split the path into segments
        segments = path_pattern.split("/")
        for segment in segments:
            if not segment:
                continue

            # Check if this is a parameter segment
            if segment.startswith(":"):
                param_name = segment[1:]
                param_names.append(param_name)
                regex_pattern += "/([^/]+)"
            else:
                regex_pattern += "/" + segment

        # Handle trailing slash
        if path_pattern.endswith("/"):
            regex_pattern += "/"

        regex_pattern += "$"

        self.regex = re.compile(regex_pattern)
        self.param_names = param_names

    def matches(self, method: str, path: str) -> bool:
        """Check if this route matches the given method and path."""
        return method == self.method and self.regex.match(path) is not None

    def extract_params(self, path: str) -> Dict[str, str]:
        """Extract parameters from the path."""
        match = self.regex.match(path)
        if not match:
            return {}

        params = {}
        for i, name in enumerate(self.param_names):
            params[name] = match.group(i + 1)

        return params

class Router:
    """
    Router for the Mono HTTP server.
    """
    def __init__(self):
        self.routes: List[Route] = []
        self.middleware: List[Middleware] = []

    def add_route(self, method: str, path: str, handler: Handler) -> None:
        """Add a route to the router."""
        self.routes.append(Route(method, path, handler))

    def get(self, path: str, handler: Handler) -> None:
        """Add a GET route."""
        self.add_route("GET", path, handler)

    def post(self, path: str, handler: Handler) -> None:
        """Add a POST route."""
        self.add_route("POST", path, handler)

    def put(self, path: str, handler: Handler) -> None:
        """Add a PUT route."""
        self.add_route("PUT", path, handler)

    def delete(self, path: str, handler: Handler) -> None:
        """Add a DELETE route."""
        self.add_route("DELETE", path, handler)

    def use(self, middleware: Middleware) -> None:
        """Add middleware to the router."""
        self.middleware.append(middleware)

    def find_route(self, method: str, path: str) -> Optional[Tuple[Route, Dict[str, str]]]:
        """Find a route that matches the given method and path."""
        for route in self.routes:
            if route.matches(method, path):
                params = route.extract_params(path)
                return route, params
        return None

    def handle_request(self, request: Request, response: Response) -> None:
        """Handle a request using the registered routes and middleware."""
        # Find a matching route
        result = self.find_route(request.method, request.path)
        if result:
            route, params = result
            request.params = params

            # Apply middleware
            if self.middleware:
                self._apply_middleware(0, request, response, route.handler)
            else:
                route.handler(request, response)
        else:
            # No route found
            response.status(HttpStatus.NOT_FOUND).text("Not Found")

    def _apply_middleware(self, index: int, request: Request, response: Response, handler: Handler) -> None:
        """Apply middleware at the given index."""
        if index >= len(self.middleware):
            # No more middleware, call the handler
            handler(request, response)
        else:
            # Call the next middleware
            middleware = self.middleware[index]

            def next_middleware():
                self._apply_middleware(index + 1, request, response, handler)

            try:
                # Try with the standard middleware signature
                middleware(request, response, next_middleware)
            except TypeError:
                # Fall back to the simple middleware signature
                middleware(request, response, lambda: next_middleware())

class HttpServer:
    """
    HTTP server for the Mono language.
    """
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self.router = Router()
        self.server_socket = None
        self.running = False
        self.threads = []

    def get(self, path: str, handler: Handler) -> None:
        """Add a GET route."""
        self.router.get(path, handler)

    def post(self, path: str, handler: Handler) -> None:
        """Add a POST route."""
        self.router.post(path, handler)

    def put(self, path: str, handler: Handler) -> None:
        """Add a PUT route."""
        self.router.put(path, handler)

    def delete(self, path: str, handler: Handler) -> None:
        """Add a DELETE route."""
        self.router.delete(path, handler)

    def use(self, middleware: Middleware) -> None:
        """Add middleware to the router."""
        self.router.use(middleware)

    def start(self) -> None:
        """Start the HTTP server."""
        if self.running:
            return

        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        print(f"Mono HTTP server listening on http://{self.host}:{self.port}")

        # Start the server in a separate thread
        server_thread = threading.Thread(target=self._server_loop)
        server_thread.daemon = True
        server_thread.start()
        self.threads.append(server_thread)

    def stop(self) -> None:
        """Stop the HTTP server."""
        if not self.running:
            return

        self.running = False

        # Close the server socket
        if self.server_socket:
            self.server_socket.close()

        # Wait for all threads to finish
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=1.0)

        self.threads = []
        print("Mono HTTP server stopped")

    def _server_loop(self) -> None:
        """Main server loop."""
        while self.running:
            try:
                # Accept a connection
                client_socket, client_address = self.server_socket.accept()

                # Handle the connection in a separate thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
                self.threads.append(client_thread)
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")

    def _handle_client(self, client_socket: socket.socket, client_address: Tuple[str, int]) -> None:
        """Handle a client connection."""
        try:
            # Receive the request
            request_data = b""
            while True:
                chunk = client_socket.recv(4096)
                request_data += chunk
                if len(chunk) < 4096 or not chunk:
                    break

            if not request_data:
                return

            # Parse the request
            request = self._parse_request(request_data.decode("utf-8"))

            # Create a response
            response = Response()

            # Handle the request
            try:
                self.router.handle_request(request, response)
            except Exception as e:
                print(f"Error handling request: {e}")
                traceback.print_exc()
                response.status(HttpStatus.INTERNAL_SERVER_ERROR).text(f"Internal Server Error: {str(e)}")

            # Send the response
            http_response = response.to_http_response()
            client_socket.sendall(http_response.encode("utf-8"))
        except Exception as e:
            print(f"Error handling client: {e}")
            traceback.print_exc()
        finally:
            # Close the client socket
            client_socket.close()

    def _parse_request(self, request_text: str) -> Request:
        """Parse an HTTP request."""
        # Split the request into lines
        lines = request_text.split("\r\n")

        # Parse the request line
        request_line = lines[0].split(" ")
        if len(request_line) < 3:
            raise ValueError("Invalid request line")

        method = request_line[0]
        path = request_line[1]

        # Parse the URL
        url_parts = urlparse(path)
        path = url_parts.path
        query_params = parse_qs(url_parts.query)

        # Parse headers
        headers = {}
        i = 1
        while i < len(lines) and lines[i]:
            header_line = lines[i]
            colon_index = header_line.find(":")
            if colon_index != -1:
                header_name = header_line[:colon_index].strip()
                header_value = header_line[colon_index + 1:].strip()
                headers[header_name] = header_value
            i += 1

        # Parse body
        body = ""
        if i < len(lines):
            body = "\r\n".join(lines[i + 1:])

        return Request(method, path, headers, body, query_params)

# Create a global HTTP server instance
http_server = HttpServer()

def get_http_server() -> HttpServer:
    """Get the global HTTP server instance."""
    return http_server
