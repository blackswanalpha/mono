#!/usr/bin/env python3

"""
Manual test script for the Mono HTTP server.
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_web_server():
    """Test the web server."""
    print("Testing web server...")
    
    # Get the path to the mono-http script
    mono_http_path = Path(__file__).parent.parent / "bin" / "mono-http"
    
    # Get the path to the web_server.mono example
    web_server_path = Path(__file__).parent.parent / "examples" / "web_server.mono"
    
    # Start the HTTP server
    server_process = subprocess.Popen(
        [str(mono_http_path), str(web_server_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    # Wait for the server to start
    time.sleep(2)
    
    # Print server output
    print("Server output:")
    for line in server_process.stdout:
        print(line.strip())
        if "Mono HTTP server listening" in line:
            break
    
    # Test the root route
    try:
        print("Testing root route...")
        response = requests.get("http://localhost:8000/")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text[:100]}...")
    except requests.exceptions.ConnectionError:
        print("Could not connect to the server")
    
    # Test the hello route
    try:
        print("Testing hello route...")
        response = requests.get("http://localhost:8000/hello")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text[:100]}...")
    except requests.exceptions.ConnectionError:
        print("Could not connect to the server")
    
    # Test the user route
    try:
        print("Testing user route...")
        response = requests.get("http://localhost:8000/users/123")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("Could not connect to the server")
    
    # Stop the server
    server_process.terminate()
    server_process.wait()

def test_rest_api():
    """Test the REST API server."""
    print("Testing REST API server...")
    
    # Get the path to the mono-http script
    mono_http_path = Path(__file__).parent.parent / "bin" / "mono-http"
    
    # Get the path to the rest_api.mono example
    rest_api_path = Path(__file__).parent.parent / "examples" / "rest_api.mono"
    
    # Start the REST API server
    server_process = subprocess.Popen(
        [str(mono_http_path), str(rest_api_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    # Wait for the server to start
    time.sleep(2)
    
    # Print server output
    print("Server output:")
    for line in server_process.stdout:
        print(line.strip())
        if "Mono HTTP server listening" in line:
            break
    
    # Test the GET /api/users route
    try:
        print("Testing GET /api/users route...")
        response = requests.get("http://localhost:8000/api/users")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("Could not connect to the server")
    
    # Test the GET /api/users/:id route
    try:
        print("Testing GET /api/users/1 route...")
        response = requests.get("http://localhost:8000/api/users/1")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("Could not connect to the server")
    
    # Stop the server
    server_process.terminate()
    server_process.wait()

if __name__ == "__main__":
    test_web_server()
    test_rest_api()
