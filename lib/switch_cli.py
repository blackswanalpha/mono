"""
Switch CLI - Command-line tool for the Switch framework

This module provides the implementation for the Switch CLI commands.
"""

import os
import sys
import argparse
import subprocess
import shutil
import json
import time
import threading
import signal
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple

# Import the Switch modules
from lib.switch_interpreter import SwitchInterpreter
from lib.mono_switch_app import SwitchApp, get_switch_app, set_switch_app
from lib.mono_switch_hmr import start_hmr_watcher

# Constants
DEFAULT_PORT = 8000
DEFAULT_HOST = "localhost"
DEFAULT_WORKERS = 1
DEFAULT_OUTPUT_DIR = "./build"
DEFAULT_TEMPLATE = "app"
DEFAULT_PLATFORM = "vercel"

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
    parser.add_argument("--env", help="Environment file to use (default: .env)")

    parsed_args = parser.parse_args(args)

    # Apply mode options
    if mode == "dev":
        parsed_args.hmr = True
        parsed_args.reload = True
        parsed_args.debug = True
    elif mode == "prod":
        parsed_args.prod = True

    # Determine the file to run
    file_path = parsed_args.app

    # If the app argument is not a file, try to find the main file
    if not os.path.isfile(file_path):
        # Check if it's a directory
        if os.path.isdir(file_path):
            # Look for app.mono or main.mono in the directory
            if os.path.isfile(os.path.join(file_path, "app.mono")):
                file_path = os.path.join(file_path, "app.mono")
            elif os.path.isfile(os.path.join(file_path, "main.mono")):
                file_path = os.path.join(file_path, "main.mono")
            else:
                print(f"Error: Could not find app.mono or main.mono in directory: {file_path}")
                return 1
        else:
            # Try to find a mono.config file in the current directory
            config_path = "mono.config"
            if os.path.isfile(config_path):
                try:
                    with open(config_path, "r") as f:
                        config = json.load(f)

                    # Get the main file from the config
                    if "main" in config:
                        file_path = config["main"]
                    else:
                        print("Error: mono.config does not specify a main file")
                        return 1
                except Exception as e:
                    print(f"Error reading mono.config: {str(e)}")
                    return 1
            else:
                print(f"Error: File not found: {file_path}")
                return 1

    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return 1

    # Load environment variables if specified
    if parsed_args.env:
        _load_env_file(parsed_args.env)
    else:
        # Try to load .env file if it exists
        if os.path.isfile(".env"):
            _load_env_file(".env")

    # Load settings from mono.config if it exists
    config_settings = {}
    config_path = "mono.config"
    if os.path.isfile(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)

            # Get settings from the config
            if "settings" in config:
                config_settings = config["settings"]
        except Exception as e:
            print(f"Warning: Error reading mono.config: {str(e)}")

    # Determine mode
    use_ssr = parsed_args.ssr or config_settings.get("ssr", False)
    use_hmr = parsed_args.hmr or config_settings.get("hmr", False)
    use_reload = parsed_args.reload or config_settings.get("reload", False)
    use_kits = not parsed_args.no_kits
    debug = parsed_args.debug or config_settings.get("debug", False)

    # Get port and host from config if not specified
    port = parsed_args.port or config_settings.get("port", DEFAULT_PORT)
    host = parsed_args.host or config_settings.get("host", DEFAULT_HOST)
    workers = parsed_args.workers or config_settings.get("workers", DEFAULT_WORKERS)

    # Production mode disables development features
    if parsed_args.prod or config_settings.get("env", "") == "production":
        use_hmr = False
        use_reload = False
        debug = False

    # Set environment variables
    os.environ["SWITCH_PORT"] = str(port)
    os.environ["SWITCH_HOST"] = host
    os.environ["SWITCH_WORKERS"] = str(workers)

    # If using multiple workers, spawn worker processes
    if workers > 1 and not use_reload:
        return _run_with_workers(file_path, workers, use_ssr, use_hmr, use_kits, debug)

    # If using live reloading, start the reloader
    if use_reload:
        return _run_with_reloader(file_path, use_ssr, use_hmr, use_kits, debug)

    # Otherwise, run the application directly
    return _run_application(file_path, use_ssr, use_hmr, use_kits, debug)

def _load_env_file(file_path: str) -> None:
    """Load environment variables from a file."""
    if not os.path.isfile(file_path):
        print(f"Warning: Environment file not found: {file_path}")
        return

    try:
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Parse the line
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # Set the environment variable
                    os.environ[key] = value
    except Exception as e:
        print(f"Warning: Error reading environment file: {str(e)}")

def _run_application(file_path: str, use_ssr: bool, use_hmr: bool, use_kits: bool, debug: bool) -> int:
    """Run a Switch application."""
    try:
        # Create the Switch interpreter
        interpreter = SwitchInterpreter(use_ssr=use_ssr, use_hmr=use_hmr, use_kits=use_kits, debug=debug)

        # Parse the file
        interpreter.parse_file(file_path)

        # Run the interpreter
        interpreter.run()

        return 0
    except KeyboardInterrupt:
        print("\nApplication stopped")
        return 0
    except Exception as e:
        if debug:
            # Print detailed error information in debug mode
            import traceback
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
        else:
            # Print simple error message in production mode
            print(f"Error: {str(e)}")
            print("Run with --debug for more information.")
        return 1

def _run_with_workers(file_path: str, num_workers: int, use_ssr: bool, use_hmr: bool, use_kits: bool, debug: bool) -> int:
    """Run a Switch application with multiple worker processes."""
    # Create worker processes
    workers = []
    for i in range(num_workers):
        # Create a worker process
        worker = subprocess.Popen([
            sys.executable,
            "-m",
            "lib.switch_worker",
            file_path,
            "--worker-id", str(i),
            *(["--ssr"] if use_ssr else []),
            *(["--hmr"] if use_hmr else []),
            *(["--no-kits"] if not use_kits else []),
            *(["--debug"] if debug else [])
        ])
        workers.append(worker)

    # Wait for all workers to finish
    try:
        for worker in workers:
            worker.wait()
        return 0
    except KeyboardInterrupt:
        # Stop all workers
        for worker in workers:
            worker.terminate()
        print("\nApplication stopped")
        return 0

def _run_with_reloader(file_path: str, use_ssr: bool, use_hmr: bool, use_kits: bool, debug: bool) -> int:
    """Run a Switch application with live reloading."""
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    # Get the directory containing the file
    directory = os.path.dirname(os.path.abspath(file_path))

    # Create a process for the application
    process = None

    # Create a handler for file changes
    class ReloadHandler(FileSystemEventHandler):
        def on_modified(self, event):
            nonlocal process

            # Only reload on .mono file changes
            if not event.is_directory and event.src_path.endswith(".mono"):
                print(f"File changed: {event.src_path}")
                print("Reloading application...")

                # Stop the current process
                if process is not None:
                    process.terminate()
                    process.wait()

                # Start a new process
                process = subprocess.Popen([
                    sys.executable,
                    "-m",
                    "lib.switch_worker",
                    file_path,
                    *(["--ssr"] if use_ssr else []),
                    *(["--hmr"] if use_hmr else []),
                    *(["--no-kits"] if not use_kits else []),
                    *(["--debug"] if debug else [])
                ])

    # Create an observer
    observer = Observer()
    observer.schedule(ReloadHandler(), directory, recursive=True)
    observer.start()

    # Start the initial process
    process = subprocess.Popen([
        sys.executable,
        "-m",
        "lib.switch_worker",
        file_path,
        *(["--ssr"] if use_ssr else []),
        *(["--hmr"] if use_hmr else []),
        *(["--no-kits"] if not use_kits else []),
        *(["--debug"] if debug else [])
    ])

    # Wait for the process to finish
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Stop the observer and process
        observer.stop()
        if process is not None:
            process.terminate()
        print("\nApplication stopped")
        return 0
    finally:
        observer.join()

def build_command(args: List[str]) -> int:
    """Build a Switch application for production."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Build a Switch application for production")
    parser.add_argument("file", help="Mono file to build")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_DIR, help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("--minify", action="store_true", help="Minify JavaScript and CSS files")
    parser.add_argument("--bundle", action="store_true", help="Bundle JavaScript and CSS files")
    parser.add_argument("--tree-shake", action="store_true", help="Remove unused code")
    parser.add_argument("--no-sourcemap", action="store_true", help="Disable source maps")
    parser.add_argument("--code-splitting", action="store_true", help="Enable code splitting")
    parser.add_argument("--differential-loading", action="store_true", help="Enable differential loading")
    parser.add_argument("--analyze", action="store_true", help="Analyze bundle size")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")

    parsed_args = parser.parse_args(args)

    # Import the build function
    from lib.switch_build import build_switch_app

    # Build the application
    success = build_switch_app(
        parsed_args.file,
        parsed_args.output,
        minify=parsed_args.minify,
        bundle=parsed_args.bundle,
        tree_shake=parsed_args.tree_shake,
        sourcemap=not parsed_args.no_sourcemap,
        code_splitting=parsed_args.code_splitting,
        differential_loading=parsed_args.differential_loading,
        analyze=parsed_args.analyze,
        verbose=parsed_args.verbose
    )

    return 0 if success else 1

def create_command(args: List[str]) -> int:
    """Create a new Switch application."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Create a new Switch application")
    parser.add_argument("name", help="Application name")
    parser.add_argument("--template", default=DEFAULT_TEMPLATE, help=f"Template to use (default: {DEFAULT_TEMPLATE})")
    parser.add_argument("--directory", default=".", help="Directory to create the application in (default: current directory)")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")

    parsed_args = parser.parse_args(args)

    # Import the create function
    from lib.switch_create import create_switch_app

    # Create the application
    success = create_switch_app(
        parsed_args.name,
        template=parsed_args.template,
        directory=parsed_args.directory,
        verbose=parsed_args.verbose
    )

    return 0 if success else 1

def deploy_command(args: List[str]) -> int:
    """Deploy a Switch application."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Deploy a Switch application")
    parser.add_argument("directory", help="Directory containing the Switch application")
    parser.add_argument("--platform", default=DEFAULT_PLATFORM, help=f"Platform to deploy to (default: {DEFAULT_PLATFORM})")
    parser.add_argument("--name", help="Project name (default: directory name)")
    parser.add_argument("--prod", action="store_true", help="Deploy to production")
    parser.add_argument("--no-build", action="store_true", help="Skip the build step")
    parser.add_argument("--no-deploy", action="store_true", help="Prepare for deployment but don't deploy")

    parsed_args = parser.parse_args(args)

    # Import the deploy function
    from lib.switch_deploy import deploy_switch_app

    # Deploy the application
    success = deploy_switch_app(
        parsed_args.directory,
        platform=parsed_args.platform,
        project_name=parsed_args.name,
        production=parsed_args.prod,
        skip_build=parsed_args.no_build,
        skip_deploy=parsed_args.no_deploy
    )

    return 0 if success else 1

def component_command(args: List[str]) -> int:
    """Generate a new component."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Generate a new component")
    parser.add_argument("name", help="Component name")
    parser.add_argument("--directory", default="components", help="Directory to create the component in (default: components)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")

    parsed_args = parser.parse_args(args)

    # Import the component function
    from lib.switch_generate import generate_component

    # Generate the component
    success = generate_component(
        parsed_args.name,
        directory=parsed_args.directory,
        force=parsed_args.force
    )

    return 0 if success else 1

def page_command(args: List[str]) -> int:
    """Generate a new page."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Generate a new page")
    parser.add_argument("name", help="Page name")
    parser.add_argument("--directory", default="pages", help="Directory to create the page in (default: pages)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")

    parsed_args = parser.parse_args(args)

    # Import the page function
    from lib.switch_generate import generate_page

    # Generate the page
    success = generate_page(
        parsed_args.name,
        directory=parsed_args.directory,
        force=parsed_args.force
    )

    return 0 if success else 1

def store_command(args: List[str]) -> int:
    """Generate a store module."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Generate a store module")
    parser.add_argument("name", help="Store module name")
    parser.add_argument("--directory", default="store", help="Directory to create the store module in (default: store)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")

    parsed_args = parser.parse_args(args)

    # Import the store function
    from lib.switch_generate import generate_store

    # Generate the store module
    success = generate_store(
        parsed_args.name,
        directory=parsed_args.directory,
        force=parsed_args.force
    )

    return 0 if success else 1
