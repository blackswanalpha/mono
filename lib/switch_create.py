"""
Switch Create - Create new Switch applications

This module provides functions for creating new Switch applications with the new project structure.
"""

import os
import sys
import shutil
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

def create_switch_app(
    name: str,
    template: str = "app",
    directory: str = ".",
    verbose: bool = False
) -> bool:
    """Create a new Switch application."""
    # Get the absolute path of the directory
    directory = os.path.abspath(directory)
    
    # Create the application directory
    app_dir = os.path.join(directory, name)
    
    if os.path.exists(app_dir):
        print(f"Error: Directory already exists: {app_dir}")
        return False
    
    os.makedirs(app_dir, exist_ok=True)
    
    if verbose:
        print(f"Creating application in {app_dir}")
    
    # Get the template directory
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "switch", template)
    
    if not os.path.isdir(template_dir):
        print(f"Error: Template not found: {template}")
        return False
    
    # Create the new project structure
    create_project_structure(app_dir, name, verbose)
    
    # Copy the template files
    copy_template_files(template_dir, app_dir, name, verbose)
    
    if verbose:
        print(f"Application created successfully: {app_dir}")
    
    return True

def create_project_structure(app_dir: str, name: str, verbose: bool = False) -> None:
    """Create the new project structure."""
    if verbose:
        print("Creating project structure...")
    
    # Create the switch.settings directory
    settings_dir = os.path.join(app_dir, "switch.settings")
    os.makedirs(settings_dir, exist_ok=True)
    
    # Create subdirectories in switch.settings
    os.makedirs(os.path.join(settings_dir, "kits"), exist_ok=True)
    os.makedirs(os.path.join(settings_dir, "pkgs"), exist_ok=True)
    os.makedirs(os.path.join(settings_dir, "jsons"), exist_ok=True)
    
    # Create the src directory
    src_dir = os.path.join(app_dir, "src")
    os.makedirs(src_dir, exist_ok=True)
    
    # Create subdirectories in src
    os.makedirs(os.path.join(src_dir, "templates"), exist_ok=True)
    os.makedirs(os.path.join(src_dir, "static"), exist_ok=True)
    os.makedirs(os.path.join(src_dir, "assets"), exist_ok=True)
    
    # Create static subdirectories
    os.makedirs(os.path.join(src_dir, "static", "css"), exist_ok=True)
    os.makedirs(os.path.join(src_dir, "static", "js"), exist_ok=True)
    os.makedirs(os.path.join(src_dir, "static", "img"), exist_ok=True)
    
    # Create assets subdirectories
    os.makedirs(os.path.join(src_dir, "assets", "fonts"), exist_ok=True)
    os.makedirs(os.path.join(src_dir, "assets", "icons"), exist_ok=True)

def copy_template_files(template_dir: str, app_dir: str, name: str, verbose: bool = False) -> None:
    """Copy template files to the application directory."""
    if verbose:
        print("Copying template files...")
    
    # Create the basic configuration files
    create_config_files(app_dir, name, verbose)
    
    # Copy template files if they exist
    for root, dirs, files in os.walk(template_dir):
        # Get the relative path from the template directory
        rel_path = os.path.relpath(root, template_dir)
        
        # Create the corresponding directory in the application
        if rel_path != ".":
            os.makedirs(os.path.join(app_dir, rel_path), exist_ok=True)
        
        # Copy the files
        for file in files:
            src_path = os.path.join(root, file)
            
            # Determine the destination path based on the file type
            if file.endswith(".mono"):
                # Mono files go to the root or appropriate subdirectory
                if "components" in rel_path:
                    dst_path = os.path.join(app_dir, "src", "components", file)
                    os.makedirs(os.path.join(app_dir, "src", "components"), exist_ok=True)
                elif "pages" in rel_path:
                    dst_path = os.path.join(app_dir, "src", "pages", file)
                    os.makedirs(os.path.join(app_dir, "src", "pages"), exist_ok=True)
                elif file == "settings.mono" or file == "route.mono" or file == "views.mono" or file == "core.mono":
                    dst_path = os.path.join(app_dir, "switch.settings", file)
                elif file == "app.mono":
                    dst_path = os.path.join(app_dir, file)
                else:
                    dst_path = os.path.join(app_dir, file)
            elif file.endswith(".css"):
                # CSS files go to static/css
                if file == "app.css":
                    dst_path = os.path.join(app_dir, file)
                else:
                    dst_path = os.path.join(app_dir, "src", "static", "css", file)
            elif file.endswith(".js"):
                # JS files go to static/js
                dst_path = os.path.join(app_dir, "src", "static", "js", file)
            elif file.endswith(".json"):
                # JSON files go to switch.settings/jsons or root
                if file == "app.json":
                    dst_path = os.path.join(app_dir, file)
                else:
                    dst_path = os.path.join(app_dir, "switch.settings", "jsons", file)
            elif file.endswith(".pkg"):
                # PKG files go to root
                dst_path = os.path.join(app_dir, file.replace("app.pkg", f"{name}.pkg"))
            elif file.endswith(".html"):
                # HTML files go to root or templates
                if file == "index.html":
                    dst_path = os.path.join(app_dir, file)
                else:
                    dst_path = os.path.join(app_dir, "src", "templates", file)
            elif file == "mono.config":
                # mono.config goes to root
                dst_path = os.path.join(app_dir, file)
            else:
                # Other files go to assets
                dst_path = os.path.join(app_dir, "src", "assets", file)
            
            # Create the destination directory if it doesn't exist
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            
            # Read the file content
            with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            # Replace template variables
            content = content.replace("{{APP_NAME}}", name)
            content = content.replace("{{APP_NAME_LOWER}}", name.lower())
            content = content.replace("{{APP_NAME_UPPER}}", name.upper())
            content = content.replace("{{APP_NAME_TITLE}}", name.title())
            
            # Write the file
            with open(dst_path, "w", encoding="utf-8") as f:
                f.write(content)

def create_config_files(app_dir: str, name: str, verbose: bool = False) -> None:
    """Create the basic configuration files."""
    if verbose:
        print("Creating configuration files...")
    
    # Create app.json
    app_json = {
        "name": name,
        "version": "1.0.0",
        "description": f"A Switch application named {name}",
        "author": "",
        "license": "MIT",
        "dependencies": {
            "switch-core": "^1.0.0",
            "switch-ui-kit": "^1.0.0"
        },
        "devDependencies": {
            "switch-dev-server": "^1.0.0"
        },
        "scripts": {
            "start": "switch run app --reload",
            "build": "switch build app --minify --bundle",
            "deploy": "switch deploy app"
        },
        "settings": {
            "port": 8000,
            "host": "localhost",
            "ssr": true,
            "hmr": true
        }
    }
    
    with open(os.path.join(app_dir, "app.json"), "w") as f:
        json.dump(app_json, f, indent=2)
    
    # Create mono.config
    mono_config = {
        "name": name,
        "version": "1.0.0",
        "type": "switch-app",
        "main": "app.mono",
        "settings": {
            "port": 8000,
            "host": "localhost",
            "workers": 1,
            "debug": true,
            "env": "development"
        },
        "paths": {
            "settings": "switch.settings",
            "src": "src",
            "static": "src/static",
            "assets": "src/assets",
            "templates": "src/templates"
        },
        "build": {
            "output": "build",
            "minify": true,
            "bundle": true,
            "sourcemap": true
        },
        "deploy": {
            "platform": "vercel",
            "env": "production"
        }
    }
    
    with open(os.path.join(app_dir, "mono.config"), "w") as f:
        json.dump(mono_config, f, indent=2)
    
    # Create package file
    pkg_content = f"""//  __  __                   
// |  \/  | ___  _ __   ___  
// | |\/| |/ _ \| '_ \ / _ \ 
// | |  | | (_) | | | | (_) |
// |_|  |_|\___/|_| |_|\___/ 
//                           
// {name} Package

package {name} {{
    version "1.0.0"
    description "A Switch application package"
    author ""
    license "MIT"
    
    // Dependencies
    depends {{
        switch-core version "^1.0.0"
        switch-ui-kit version "^1.0.0"
    }}
    
    // Components
    collect {{
        App from "app.mono"
        HomePage from "src/pages/home.mono"
        AboutPage from "src/pages/about.mono"
    }}
    
    // Settings
    settings {{
        port 8000
        host "localhost"
        workers 1
        debug true
    }}
}}
"""
    
    with open(os.path.join(app_dir, f"{name}.pkg"), "w") as f:
        f.write(pkg_content)
    
    # Create settings.mono
    settings_mono = """//  __  __                   
// |  \/  | ___  _ __   ___  
// | |\/| |/ _ \| '_ \ / _ \ 
// | |  | | (_) | | | | (_) |
// |_|  |_|\___/|_| |_|\___/ 
//                           
// Switch Settings

// Import required modules
import "core.mono"
import "route.mono"
import "views.mono"

// Application settings
settings {
    // Server settings
    server {
        port 8000
        host "localhost"
        workers 1
        debug true
    }
    
    // Application settings
    app {
        name "{{APP_NAME}}"
        version "1.0.0"
        description "A Switch application"
    }
    
    // Environment settings
    env {
        development {
            debug true
            hmr true
            ssr true
        }
        production {
            debug false
            hmr false
            ssr true
        }
    }
    
    // Static file settings
    static {
        path "src/static"
        url "/static"
    }
    
    // Template settings
    templates {
        path "src/templates"
        engine "switch"
    }
}
"""
    
    with open(os.path.join(app_dir, "switch.settings", "settings.mono"), "w") as f:
        f.write(settings_mono)
    
    # Create route.mono
    route_mono = """//  __  __                   
// |  \/  | ___  _ __   ___  
// | |\/| |/ _ \| '_ \ / _ \ 
// | |  | | (_) | | | | (_) |
// |_|  |_|\___/|_| |_|\___/ 
//                           
// Switch Routes

// Define routes
routes {
    // Home page
    get "/" {
        render "home" {
            title "{{APP_NAME}} - Home"
            scripts ["/static/js/app.js"]
            styles ["/static/css/app.css"]
        }
    }
    
    // About page
    get "/about" {
        render "about" {
            title "{{APP_NAME}} - About"
            scripts ["/static/js/app.js"]
            styles ["/static/css/app.css"]
        }
    }
    
    // API routes
    group "/api" {
        // Get data
        get "/data" {
            json {
                status "success"
                data [
                    { id: 1, name: "Item 1" },
                    { id: 2, name: "Item 2" },
                    { id: 3, name: "Item 3" }
                ]
            }
        }
        
        // Post data
        post "/data" {
            // Get request body
            var data = req.body
            
            // Return response
            json {
                status "success"
                message "Data received"
                data data
            }
        }
    }
    
    // Static files
    get "/static/(.*)" {
        static "src/static"
    }
}
"""
    
    with open(os.path.join(app_dir, "switch.settings", "route.mono"), "w") as f:
        f.write(route_mono)
    
    # Create views.mono
    views_mono = """//  __  __                   
// |  \/  | ___  _ __   ___  
// | |\/| |/ _ \| '_ \ / _ \ 
// | |  | | (_) | | | | (_) |
// |_|  |_|\___/|_| |_|\___/ 
//                           
// Switch Views

// Define views
views {
    // Home view
    view "home" {
        component "App" {
            props {
                currentPage "home"
            }
        }
    }
    
    // About view
    view "about" {
        component "App" {
            props {
                currentPage "about"
            }
        }
    }
}
"""
    
    with open(os.path.join(app_dir, "switch.settings", "views.mono"), "w") as f:
        f.write(views_mono)
    
    # Create core.mono
    core_mono = """//  __  __                   
// |  \/  | ___  _ __   ___  
// | |\/| |/ _ \| '_ \ / _ \ 
// | |  | | (_) | | | | (_) |
// |_|  |_|\___/|_| |_|\___/ 
//                           
// Switch Core

// Import kits
import kits {
    SwitchUIKit version "^1.0.0"
}

// Import packages
import pkgs {
    http-client version "^1.0.0"
    date-formatter version "^1.0.0"
}

// Define global variables
globals {
    APP_NAME "{{APP_NAME}}"
    APP_VERSION "1.0.0"
    API_URL "/api"
}

// Define middleware
middleware {
    // Logger middleware
    use "logger" {
        level "info"
        format "[%date%] %method% %url% - %status%"
    }
    
    // CORS middleware
    use "cors" {
        origin "*"
        methods ["GET", "POST", "PUT", "DELETE"]
        headers ["Content-Type", "Authorization"]
    }
    
    // Body parser middleware
    use "body-parser" {
        json true
        urlencoded true
    }
}
"""
    
    with open(os.path.join(app_dir, "switch.settings", "core.mono"), "w") as f:
        f.write(core_mono)
