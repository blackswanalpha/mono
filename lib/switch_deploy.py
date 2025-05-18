"""
Switch Deploy - Deploy Switch applications to various platforms

This module provides functions for deploying Switch applications to various platforms.
It supports:
1. Vercel
2. Netlify
3. AWS
"""

import os
import sys
import shutil
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

def deploy_switch_app(
    directory: str,
    platform: str = "vercel",
    project_name: Optional[str] = None,
    production: bool = False,
    skip_build: bool = False,
    skip_deploy: bool = False
) -> bool:
    """Deploy a Switch application to a platform."""
    # Get the absolute path of the directory
    directory = os.path.abspath(directory)
    
    # Check if the directory exists
    if not os.path.exists(directory):
        print(f"Error: Directory not found: {directory}")
        return False
    
    # Use the directory name as the project name if not provided
    if not project_name:
        project_name = os.path.basename(directory)
    
    print(f"Deploying {project_name} to {platform}...")
    
    # Prepare the deployment
    if platform == "vercel":
        success = _prepare_vercel_deployment(directory, project_name, skip_build)
    elif platform == "netlify":
        success = _prepare_netlify_deployment(directory, project_name, skip_build)
    elif platform == "aws":
        success = _prepare_aws_deployment(directory, project_name, skip_build)
    else:
        print(f"Error: Unsupported platform: {platform}")
        return False
    
    if not success:
        return False
    
    # Skip deployment if requested
    if skip_deploy:
        print(f"Deployment preparation completed: {directory}")
        return True
    
    # Deploy the application
    if platform == "vercel":
        return _deploy_to_vercel(directory, project_name, production)
    elif platform == "netlify":
        return _deploy_to_netlify(directory, project_name, production)
    elif platform == "aws":
        return _deploy_to_aws(directory, project_name, production)
    else:
        print(f"Error: Unsupported platform: {platform}")
        return False

def _prepare_vercel_deployment(directory: str, project_name: str, skip_build: bool) -> bool:
    """Prepare a Switch application for deployment to Vercel."""
    print(f"Preparing {project_name} for deployment to Vercel...")
    
    # Create the deployment directory structure
    deploy_dir = os.path.join(directory, ".vercel")
    api_dir = os.path.join(deploy_dir, "api")
    public_dir = os.path.join(deploy_dir, "public")
    static_dir = os.path.join(public_dir, "static")
    
    # Create directories
    os.makedirs(deploy_dir, exist_ok=True)
    os.makedirs(api_dir, exist_ok=True)
    os.makedirs(public_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)
    
    # Copy the vercel.json template
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    vercel_template = os.path.join(template_dir, "vercel.json")
    
    if os.path.exists(vercel_template):
        shutil.copy(vercel_template, os.path.join(directory, "vercel.json"))
    else:
        # Create vercel.json if template doesn't exist
        vercel_config = {
            "version": 2,
            "builds": [
                {
                    "src": "api/**/*.py",
                    "use": "@vercel/python"
                },
                {
                    "src": "public/**/*",
                    "use": "@vercel/static"
                }
            ],
            "routes": [
                {
                    "src": "/api/(.*)",
                    "dest": "/api/$1"
                },
                {
                    "src": "/static/(.*)",
                    "dest": "/public/static/$1"
                },
                {
                    "src": "/(.*)",
                    "dest": "/api/index.py"
                }
            ],
            "env": {
                "MONO_ENV": "production"
            }
        }
        
        with open(os.path.join(directory, "vercel.json"), "w") as f:
            json.dump(vercel_config, f, indent=2)
    
    # Create requirements.txt
    with open(os.path.join(directory, "requirements.txt"), "w") as f:
        f.write("watchdog==2.1.9\n")
    
    # Create the API handler
    api_handler_template = os.path.join(template_dir, "vercel_api_handler.py")
    api_handler_path = os.path.join(api_dir, "index.py")
    
    if os.path.exists(api_handler_template):
        shutil.copy(api_handler_template, api_handler_path)
    else:
        # Create the API handler if template doesn't exist
        with open(api_handler_path, "w") as f:
            f.write("""
from http.server import BaseHTTPRequestHandler
import os
import sys
import json
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Try to import the Mono Switch framework
try:
    from lib.mono_switch import SwitchComponent, SwitchRenderer
    from lib.mono_http import Request, Response, HttpStatus
    
    # Flag to indicate that the framework is loaded
    FRAMEWORK_LOADED = True
except ImportError:
    # If the framework is not found, create a minimal implementation
    FRAMEWORK_LOADED = False
    
    class SwitchComponent:
        def __init__(self, name, props=None):
            self.name = name
            self.props = props or {}
        
        def to_json(self):
            return json.dumps({
                "name": self.name,
                "props": self.props
            })
    
    class SwitchRenderer:
        def __init__(self, title, scripts=None, styles=None):
            self.title = title
            self.scripts = scripts or []
            self.styles = styles or []
        
        def render(self, component):
            return f"<html><head><title>{self.title}</title></head><body><h1>{component.name}</h1></body></html>"
    
    class HttpStatus:
        OK = 200
        NOT_FOUND = 404
        INTERNAL_SERVER_ERROR = 500
    
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
        
        def text(self, text):
            self.body = text
            return self
        
        def html(self, html):
            self.header("Content-Type", "text/html")
            self.body = html
            return self
        
        def json(self, data):
            self.header("Content-Type", "application/json")
            self.body = json.dumps(data)
            return self
    
    class Request:
        def __init__(self, method, path, headers=None, body=""):
            self.method = method
            self.path = path
            self.headers = headers or {}
            self.body = body
            self.params = {}
            self.query = {}

# Find the main Mono file
main_file = None
for file in os.listdir(Path(__file__).resolve().parent.parent.parent):
    if file.endswith(".mono") and "main" in file.lower():
        main_file = file
        break

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Create a request object
        request = Request(
            method="GET",
            path=self.path,
            headers=dict(self.headers)
        )
        
        # Create a response object
        response = Response()
        
        # Handle the request
        if main_file:
            # If we found a main file, render a placeholder
            component = SwitchComponent("App", {"title": "Mono Switch App"})
            renderer = SwitchRenderer("Mono Switch App")
            html = renderer.render(component)
            response.html(html)
        else:
            # Otherwise, show an error
            response.status(HttpStatus.NOT_FOUND)
            response.html("<h1>404 Not Found</h1><p>No Mono application found.</p>")
        
        # Send the response
        self.send_response(response.status_code)
        
        # Send headers
        for name, value in response.headers.items():
            self.send_header(name, value)
        self.end_headers()
        
        # Send body
        self.wfile.write(response.body.encode("utf-8"))
""")
    
    # Build the application if needed
    if not skip_build:
        print("Building the application...")
        
        # Find the main Mono file
        main_file = None
        for file in os.listdir(directory):
            if file.endswith(".mono") and "main" in file.lower():
                main_file = file
                break
        
        if main_file:
            # Run the build command
            build_cmd = ["switch", "build", "--minify", "--bundle", os.path.join(directory, main_file)]
            try:
                subprocess.run(build_cmd, check=True, cwd=directory)
                print("Build completed successfully.")
            except subprocess.CalledProcessError:
                print("Error: Build failed.")
                return False
        else:
            print("Warning: No main Mono file found. Skipping build step.")
    
    # Copy static files to the public directory
    static_src_dir = os.path.join(directory, "static")
    if os.path.isdir(static_src_dir):
        for root, _, files in os.walk(static_src_dir):
            for file in files:
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, static_src_dir)
                dst_path = os.path.join(static_dir, rel_path)
                
                # Create the destination directory if it doesn't exist
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                
                # Copy the file
                shutil.copy2(src_path, dst_path)
    
    # Copy the build directory to the public directory
    build_dir = os.path.join(directory, "build")
    if os.path.isdir(build_dir):
        for root, _, files in os.walk(build_dir):
            for file in files:
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, build_dir)
                dst_path = os.path.join(public_dir, rel_path)
                
                # Create the destination directory if it doesn't exist
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                
                # Copy the file
                shutil.copy2(src_path, dst_path)
    
    print(f"Vercel deployment preparation completed: {directory}")
    return True

def _deploy_to_vercel(directory: str, project_name: str, production: bool) -> bool:
    """Deploy a Switch application to Vercel."""
    # Get the absolute path of the directory
    directory = os.path.abspath(directory)
    
    # Check if Vercel CLI is installed
    try:
        subprocess.run(["vercel", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Vercel CLI not found. Please install it with 'npm install -g vercel'.")
        return False
    
    # Build the deployment command
    deploy_cmd = ["vercel"]
    
    if project_name:
        deploy_cmd.extend(["--name", project_name])
    
    if production:
        deploy_cmd.append("--prod")
    
    # Run the deployment command
    try:
        print("Deploying to Vercel...")
        subprocess.run(deploy_cmd, check=True, cwd=directory)
        print("Deployment completed successfully.")
        return True
    except subprocess.CalledProcessError:
        print("Error: Deployment failed.")
        return False

def _prepare_netlify_deployment(directory: str, project_name: str, skip_build: bool) -> bool:
    """Prepare a Switch application for deployment to Netlify."""
    print(f"Preparing {project_name} for deployment to Netlify...")
    
    # TODO: Implement Netlify deployment preparation
    
    print(f"Netlify deployment preparation completed: {directory}")
    return True

def _deploy_to_netlify(directory: str, project_name: str, production: bool) -> bool:
    """Deploy a Switch application to Netlify."""
    # TODO: Implement Netlify deployment
    
    print("Netlify deployment not yet implemented.")
    return False

def _prepare_aws_deployment(directory: str, project_name: str, skip_build: bool) -> bool:
    """Prepare a Switch application for deployment to AWS."""
    print(f"Preparing {project_name} for deployment to AWS...")
    
    # TODO: Implement AWS deployment preparation
    
    print(f"AWS deployment preparation completed: {directory}")
    return True

def _deploy_to_aws(directory: str, project_name: str, production: bool) -> bool:
    """Deploy a Switch application to AWS."""
    # TODO: Implement AWS deployment
    
    print("AWS deployment not yet implemented.")
    return False
