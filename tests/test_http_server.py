#!/usr/bin/env python3

"""
Test script for the Mono HTTP server.
"""

import os
import sys
import unittest
import requests
import subprocess
import time
import signal
import json
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Start the HTTP server before running the tests
def start_server(script_path):
    """Start a Mono HTTP server."""
    mono_http_path = Path(__file__).parent.parent / "bin" / "mono-http"
    script_path = Path(__file__).parent.parent / "examples" / script_path

    # Start the server
    process = subprocess.Popen(
        [str(mono_http_path), str(script_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

    # Wait for the server to start
    time.sleep(2)

    return process

# Start the web server
print("Starting web server...")
web_server = start_server("web_server.mono")

# Wait for the server to be ready
time.sleep(2)

# Print server output
print("Web server output:")
for line in web_server.stdout:
    print(line.strip())
    if "Mono HTTP server listening" in line:
        break

class TestHttpServer(unittest.TestCase):
    """Test the Mono HTTP server."""

    def test_root_route(self):
        """Test the root route."""
        try:
            response = requests.get("http://localhost:8000/")
            self.assertEqual(response.status_code, 200)
            self.assertIn("Welcome to Mono Web Server", response.text)
        except requests.exceptions.ConnectionError:
            self.fail("Could not connect to the server")

    def test_hello_route(self):
        """Test the hello route."""
        try:
            response = requests.get("http://localhost:8000/hello")
            self.assertEqual(response.status_code, 200)
            self.assertIn("Hello, World!", response.text)

            response = requests.get("http://localhost:8000/hello?name=John")
            self.assertEqual(response.status_code, 200)
            self.assertIn("Hello, John!", response.text)
        except requests.exceptions.ConnectionError:
            self.fail("Could not connect to the server")

    def test_user_route(self):
        """Test the user route."""
        try:
            response = requests.get("http://localhost:8000/users/123")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["id"], "123")
            self.assertEqual(data["name"], "User 123")
            self.assertEqual(data["email"], "user123@example.com")
        except requests.exceptions.ConnectionError:
            self.fail("Could not connect to the server")

# Stop the web server
web_server.terminate()
web_server.wait()

# Start the REST API server
print("Starting REST API server...")
rest_api_server = start_server("rest_api.mono")

# Wait for the server to be ready
time.sleep(2)

# Print server output
print("REST API server output:")
for line in rest_api_server.stdout:
    print(line.strip())
    if "Mono HTTP server listening" in line:
        break

class TestRestApiServer(unittest.TestCase):
    """Test the REST API server."""

    def test_get_users(self):
        """Test the GET /api/users route."""
        try:
            response = requests.get("http://localhost:8000/api/users")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(len(data), 3)
            self.assertEqual(data[0]["id"], "1")
            self.assertEqual(data[0]["name"], "John Doe")
            self.assertEqual(data[0]["email"], "john@example.com")
        except requests.exceptions.ConnectionError:
            self.fail("Could not connect to the server")

    def test_get_user(self):
        """Test the GET /api/users/:id route."""
        try:
            response = requests.get("http://localhost:8000/api/users/1")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["id"], "1")
            self.assertEqual(data["name"], "John Doe")
            self.assertEqual(data["email"], "john@example.com")
        except requests.exceptions.ConnectionError:
            self.fail("Could not connect to the server")

# Define a cleanup function to stop the server
def cleanup():
    """Stop the REST API server."""
    rest_api_server.terminate()
    rest_api_server.wait()

# Register the cleanup function to be called when the script exits
import atexit
atexit.register(cleanup)

if __name__ == "__main__":
    try:
        unittest.main()
    finally:
        # Make sure the server is stopped
        cleanup()
