"""
Switch Command - Command-line tool for the Switch framework

This module provides the implementation for the `switch` command.
"""

import os
import sys
import argparse
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple

# Templates directory
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates", "switch")

# Default settings
DEFAULT_PORT = 8000
DEFAULT_HOST = "localhost"
DEFAULT_WORKERS = 1

def show_help(command=None):
    """Show help information."""
    if command is None:
        print("""
Switch - Command-line tool for the Switch framework

Usage:
    switch <command> [options] [arguments]

Commands:
    run         Run a Switch application
    build       Build a Switch application for production
    create      Create a new Switch application
    deploy      Deploy a Switch application
    component   Generate a new component
    page        Generate a new page
    store       Generate a store module
    pkg         Manage packages
    kit         Manage kits
    help        Show help information

Run 'switch help <command>' for more information on a specific command.
""")
        return
    
    # Show help for a specific command
    if command == "run":
        print("""
Switch Run - Run a Switch application

Usage:
    switch run [options] <app>
    switch run dev <app>
    switch run prod <app>

Arguments:
    app               Application name or file to run

Options:
    --port PORT       Port to run the server on (default: 8000)
    --host HOST       Host to run the server on (default: localhost)
    --ssr             Enable server-side rendering
    --hmr             Enable hot module replacement
    --reload          Enable live reloading
    --workers N       Number of worker processes (default: 1)
    --debug           Enable debug mode
    --no-kits         Disable kit integration
    --env FILE        Environment file to use (default: .env)

Shortcuts:
    dev               Shortcut for --hmr --reload --debug
    prod              Shortcut for --prod
""")
    elif command == "build":
        print("""
Switch Build - Build a Switch application for production

Usage:
    switch build [options] <app>

Arguments:
    app               Application name or file to build

Options:
    --output DIR      Output directory (default: dist)
    --minify          Minify the output
    --sourcemaps      Generate source maps
    --no-kits         Disable kit integration
    --verbose         Show verbose output
""")
    elif command == "create":
        print("""
Switch Create - Create a new Switch application

Usage:
    switch create [options] <name>

Arguments:
    name              Application name

Options:
    --template NAME   Template to use (default: app)
                      Available templates: app, dashboard
    --directory DIR   Directory to create the application in (default: current directory)
    --dev             Create a development-ready application with additional tools
    --verbose         Show verbose output
""")
    else:
        print(f"Unknown command: {command}")
        print("Run 'switch help' for a list of commands.")

def run_command(args: List[str]) -> int:
    """Run a Switch application."""
    # Check if the first argument is "dev" or "prod"
    mode = None
    if args and args[0] in ["dev", "prod"]:
        mode = args.pop(0)
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Run a Switch application")
    parser.add_argument("app", help="Application name or file to run")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port to run the server on (default: {DEFAULT_PORT})")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Host to run the server on (default: {DEFAULT_HOST})")
    parser.add_argument("--ssr", action="store_true", help="Enable server-side rendering")
    parser.add_argument("--hmr", action="store_true", help="Enable hot module replacement")
    parser.add_argument("--reload", action="store_true", help="Enable live reloading")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help=f"Number of worker processes (default: {DEFAULT_WORKERS})")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--no-kits", action="store_true", help="Disable kit integration")
    parser.add_argument("--prod", action="store_true", help="Enable production mode")
    parser.add_argument("--env", default=".env", help="Environment file to use (default: .env)")
    
    parsed_args = parser.parse_args(args)
    
    # Apply mode options
    if mode == "dev":
        parsed_args.hmr = True
        parsed_args.reload = True
        parsed_args.debug = True
    elif mode == "prod":
        parsed_args.prod = True
    
    # Determine the file to run
    app = parsed_args.app
    if app == "app":
        # Look for main.mono in the current directory
        if os.path.exists("main.mono"):
            file_path = "main.mono"
        else:
            print("Error: main.mono not found in the current directory")
            return 1
    elif os.path.exists(app):
        # Use the provided file
        file_path = app
    else:
        print(f"Error: File not found: {app}")
        return 1
    
    # Set environment variables
    os.environ["SWITCH_PORT"] = str(parsed_args.port)
    os.environ["SWITCH_HOST"] = parsed_args.host
    os.environ["SWITCH_WORKERS"] = str(parsed_args.workers)
    
    # Determine mode
    use_ssr = parsed_args.ssr
    use_hmr = parsed_args.hmr
    use_reload = parsed_args.reload
    use_kits = not parsed_args.no_kits
    debug = parsed_args.debug
    
    # Production mode disables development features
    if parsed_args.prod:
        use_hmr = False
        use_reload = False
        debug = False
    
    # Run the application using mono-switch
    cmd = [
        "mono-switch",
        file_path
    ]
    
    if use_ssr:
        cmd.append("--ssr")
    if use_hmr:
        cmd.append("--hmr")
    if debug:
        cmd.append("--debug")
    if not use_kits:
        cmd.append("--no-kits")
    if parsed_args.prod:
        cmd.append("--prod")
    
    # Run the command
    try:
        return subprocess.call(cmd)
    except KeyboardInterrupt:
        print("\nApplication stopped")
        return 0

def build_command(args: List[str]) -> int:
    """Build a Switch application for production."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Build a Switch application for production")
    parser.add_argument("app", help="Application name or file to build")
    parser.add_argument("--output", default="dist", help="Output directory (default: dist)")
    parser.add_argument("--minify", action="store_true", help="Minify the output")
    parser.add_argument("--sourcemaps", action="store_true", help="Generate source maps")
    parser.add_argument("--no-kits", action="store_true", help="Disable kit integration")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    
    parsed_args = parser.parse_args(args)
    
    # TODO: Implement build command
    print("Building application...")
    print(f"App: {parsed_args.app}")
    print(f"Output directory: {parsed_args.output}")
    print(f"Minify: {parsed_args.minify}")
    print(f"Source maps: {parsed_args.sourcemaps}")
    print(f"Use kits: {not parsed_args.no_kits}")
    print(f"Verbose: {parsed_args.verbose}")
    
    return 0

def create_command(args: List[str]) -> int:
    """Create a new Switch application."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Create a new Switch application")
    parser.add_argument("name", help="Application name")
    parser.add_argument("--template", default="app", help="Template to use (default: app)")
    parser.add_argument("--directory", default=".", help="Directory to create the application in (default: current directory)")
    parser.add_argument("--dev", action="store_true", help="Create a development-ready application with additional tools")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    
    parsed_args = parser.parse_args(args)
    
    # Validate the application name
    app_name = parsed_args.name
    if not app_name.isalnum() and not app_name.replace("-", "").replace("_", "").isalnum():
        print(f"Error: Invalid application name: {app_name}")
        print("Application name must contain only alphanumeric characters, hyphens, and underscores.")
        return 1
    
    # Validate the template
    template = parsed_args.template
    template_dir = os.path.join(TEMPLATES_DIR, template)
    if not os.path.exists(template_dir):
        print(f"Error: Template not found: {template}")
        print("Available templates:")
        for template_name in os.listdir(TEMPLATES_DIR):
            if os.path.isdir(os.path.join(TEMPLATES_DIR, template_name)):
                print(f"  - {template_name}")
        return 1
    
    # Create the application directory
    app_dir = os.path.join(parsed_args.directory, app_name)
    if os.path.exists(app_dir):
        print(f"Error: Directory already exists: {app_dir}")
        return 1
    
    # Create the application directory
    os.makedirs(app_dir)
    
    # Create the application structure
    os.makedirs(os.path.join(app_dir, "src", "components"))
    os.makedirs(os.path.join(app_dir, "src", "pages"))
    os.makedirs(os.path.join(app_dir, "src", "static", "js"))
    os.makedirs(os.path.join(app_dir, "src", "static", "css"))
    os.makedirs(os.path.join(app_dir, "src", "static", "img"))
    os.makedirs(os.path.join(app_dir, "src", "templates"))
    
    # Copy template files
    for root, dirs, files in os.walk(template_dir):
        # Get the relative path
        rel_path = os.path.relpath(root, template_dir)
        
        # Create the target directory
        target_dir = os.path.join(app_dir, rel_path)
        if rel_path != "." and not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        # Copy files
        for file in files:
            # Get the source and target paths
            src_path = os.path.join(root, file)
            target_path = os.path.join(target_dir, file)
            
            # Read the file content
            with open(src_path, "r") as f:
                content = f.read()
            
            # Replace placeholders
            content = content.replace("{{APP_NAME}}", app_name)
            
            # Write the file
            with open(target_path, "w") as f:
                f.write(content)
            
            if parsed_args.verbose:
                print(f"Created {target_path}")
    
    # Create additional files for development mode
    if parsed_args.dev:
        # Create a run.py script
        run_script = os.path.join(app_dir, "run.py")
        with open(run_script, "w") as f:
            f.write("""#!/usr/bin/env python3
\"\"\"
Run Switch Application - Simple script to run a Switch application
\"\"\"

import os
import sys
import subprocess
import time
from pathlib import Path

def main():
    \"\"\"Run the Switch application.\"\"\"
    # Get the file to run
    file_path = "main.mono"
    
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return 1
    
    # Start the HTTP server
    process = subprocess.Popen([
        "python3",
        "-c",
        \"\"\"
import os
import sys
import http.server
import socketserver
import threading
import json

# Set up the HTTP server
PORT = 8000

# Create a custom handler that serves our app
class SwitchHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Map /static/ to src/static/
        if path.startswith('/static/'):
            return os.path.join(os.getcwd(), 'src' + path)
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
    <title>{app_name}</title>
    
    <!-- Switch Framework Styles -->
    <link rel="stylesheet" href="/static/css/switch.css">
    <link rel="stylesheet" href="/static/css/ui.css">
    <link rel="stylesheet" href="/static/css/app.css">
    
    <!-- Initial Component Data -->
    <script>
        window.SWITCH_INITIAL_DATA = {{
            name: "App",
            props: {{
                title: "{app_name}",
                currentPage: "home"
            }}
        }};
        
        window.SWITCH_ENV = {{
            debug: true,
            hmr: true,
            ssr: false
        }};
    </script>
</head>
<body>
    <!-- Root Element -->
    <div id="switch-root"></div>
    
    <!-- Switch Framework Scripts -->
    <script src="/static/js/dom.js"></script>
    <script src="/static/js/switch.js"></script>
    <script src="/static/js/store.js"></script>
    <script src="/static/js/components.js"></script>
    <script src="/static/js/ssr.js"></script>
    <script src="/static/js/ui.js"></script>
    <script src="/static/js/app.js"></script>
    
    <!-- Initialize Component -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // Create the component
            const component = Switch.createComponent(window.SWITCH_INITIAL_DATA);
            
            // Render the component
            Switch.renderComponent(component, document.getElementById('switch-root'));
            
            // Enable HMR if configured
            if (window.SWITCH_ENV.hmr && window.Switch.hmr) {{
                Switch.hmr.enable({{
                    debug: window.SWITCH_ENV.debug
                }});
            }}
        }});
    </script>
</body>
</html>'''.format(app_name="{app_name}")
        
        self.wfile.write(html.encode())

# Create the server
with socketserver.TCPServer(("", PORT), SwitchHandler) as httpd:
    print(f"Serving at http://localhost:{{PORT}}")
    httpd.serve_forever()
        \"\"\"
    ])
    
    # Wait for the server to start
    time.sleep(1)
    
    # Open the browser
    try:
        import webbrowser
        webbrowser.open(f"http://localhost:8000")
    except:
        print("Please open your browser and navigate to http://localhost:8000")
    
    # Wait for the server to finish
    try:
        process.wait()
        return 0
    except KeyboardInterrupt:
        # Stop the server
        process.terminate()
        print("\\nApplication stopped")
        return 0

if __name__ == "__main__":
    sys.exit(main())
""".replace("{app_name}", app_name))
        
        # Make the script executable
        os.chmod(run_script, 0o755)
        
        if parsed_args.verbose:
            print(f"Created {run_script}")
    
    # Print success message
    print(f"Created new Switch application: {app_name}")
    print(f"To run the application:")
    print(f"  cd {app_name}")
    if parsed_args.dev:
        print(f"  python3 run.py")
    else:
        print(f"  switch run app")
    
    return 0

def deploy_command(args: List[str]) -> int:
    """Deploy a Switch application."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Deploy a Switch application")
    parser.add_argument("directory", help="Directory containing the Switch application")
    parser.add_argument("--platform", default="vercel", help="Platform to deploy to (default: vercel)")
    parser.add_argument("--name", help="Project name (default: directory name)")
    parser.add_argument("--prod", action="store_true", help="Deploy to production")
    parser.add_argument("--no-build", action="store_true", help="Skip the build step")
    parser.add_argument("--no-deploy", action="store_true", help="Prepare for deployment but don't deploy")
    
    parsed_args = parser.parse_args(args)
    
    # TODO: Implement deploy command
    print("Deploying application...")
    print(f"Directory: {parsed_args.directory}")
    print(f"Platform: {parsed_args.platform}")
    print(f"Name: {parsed_args.name or os.path.basename(parsed_args.directory)}")
    print(f"Production: {parsed_args.prod}")
    print(f"Skip build: {parsed_args.no_build}")
    print(f"Skip deploy: {parsed_args.no_deploy}")
    
    return 0

def component_command(args: List[str]) -> int:
    """Generate a new component."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Generate a new component")
    parser.add_argument("name", help="Component name")
    parser.add_argument("--directory", default="src/components", help="Directory to create the component in (default: src/components)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    
    parsed_args = parser.parse_args(args)
    
    # TODO: Implement component command
    print("Generating component...")
    print(f"Name: {parsed_args.name}")
    print(f"Directory: {parsed_args.directory}")
    print(f"Force: {parsed_args.force}")
    
    return 0

def page_command(args: List[str]) -> int:
    """Generate a new page."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Generate a new page")
    parser.add_argument("name", help="Page name")
    parser.add_argument("--directory", default="src/pages", help="Directory to create the page in (default: src/pages)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    
    parsed_args = parser.parse_args(args)
    
    # TODO: Implement page command
    print("Generating page...")
    print(f"Name: {parsed_args.name}")
    print(f"Directory: {parsed_args.directory}")
    print(f"Force: {parsed_args.force}")
    
    return 0

def store_command(args: List[str]) -> int:
    """Generate a store module."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Generate a store module")
    parser.add_argument("name", help="Store module name")
    parser.add_argument("--directory", default="src/store", help="Directory to create the store module in (default: src/store)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    
    parsed_args = parser.parse_args(args)
    
    # TODO: Implement store command
    print("Generating store module...")
    print(f"Name: {parsed_args.name}")
    print(f"Directory: {parsed_args.directory}")
    print(f"Force: {parsed_args.force}")
    
    return 0
