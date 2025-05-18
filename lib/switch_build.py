"""
Switch Build - Build Switch applications for production

This module provides functions for building Switch applications for production.
It handles:
1. Bundling JavaScript and CSS files
2. Minifying JavaScript and CSS files
3. Tree-shaking unused code
4. Generating source maps
5. Analyzing bundle size
"""

import os
import sys
import shutil
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple, Set

# Import the Switch modules
from lib.switch_interpreter import SwitchInterpreter
from lib.mono_switch_app import SwitchApp, get_switch_app, set_switch_app

# Try to import optional dependencies
try:
    import terser
    TERSER_AVAILABLE = True
except ImportError:
    TERSER_AVAILABLE = False

try:
    import csscompressor
    CSS_COMPRESSOR_AVAILABLE = True
except ImportError:
    CSS_COMPRESSOR_AVAILABLE = False

try:
    import rollup
    ROLLUP_AVAILABLE = True
except ImportError:
    ROLLUP_AVAILABLE = False

def build_switch_app(
    file_path: str,
    output_dir: str,
    minify: bool = False,
    bundle: bool = False,
    tree_shake: bool = False,
    sourcemap: bool = True,
    code_splitting: bool = False,
    differential_loading: bool = False,
    analyze: bool = False,
    verbose: bool = False
) -> bool:
    """Build a Switch application for production."""
    # Get the absolute paths
    file_path = os.path.abspath(file_path)
    output_dir = os.path.abspath(output_dir)

    if verbose:
        print(f"Building {file_path} to {output_dir}")

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Create a Switch interpreter with production settings
    interpreter = SwitchInterpreter(use_ssr=True, use_hmr=False, use_kits=True, debug=False)

    # Get the application directory
    app_dir = os.path.dirname(file_path)

    # Create a Switch application
    app = SwitchApp(use_ssr=True, use_hmr=False, debug=False)

    # Set the static directory if it exists
    static_dir = os.path.join(app_dir, "static")
    if os.path.isdir(static_dir):
        app.set_static_dir(static_dir)

    # Set the build directory
    app.set_build_dir(output_dir)

    # Set the global application
    set_switch_app(app)

    # Run the application to initialize it
    if verbose:
        print("Running the application...")

    try:
        interpreter.run_file(file_path)
    except Exception as e:
        print(f"Error running the application: {e}")
        return False

    # Build the application
    if verbose:
        print("Building the application...")

    try:
        app.build(output_dir)
    except Exception as e:
        print(f"Error building the application: {e}")
        return False

    # Copy the Switch framework files
    if verbose:
        print("Copying framework files...")

    switch_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "switch")
    output_switch_dir = os.path.join(output_dir, "switch")

    os.makedirs(output_switch_dir, exist_ok=True)

    # Copy the core Switch files
    for file in ["switch.js", "store.js", "components.js", "switch.css", "hydrate.js"]:
        src_path = os.path.join(switch_dir, file)
        dst_path = os.path.join(output_switch_dir, file)

        if os.path.isfile(src_path):
            shutil.copy2(src_path, dst_path)

    # Copy the component files
    components_dir = os.path.join(switch_dir, "components")
    output_components_dir = os.path.join(output_switch_dir, "components")

    if os.path.isdir(components_dir):
        os.makedirs(output_components_dir, exist_ok=True)

        for file in os.listdir(components_dir):
            if file.endswith(".js"):
                src_path = os.path.join(components_dir, file)
                dst_path = os.path.join(output_components_dir, file)

                shutil.copy2(src_path, dst_path)

    # Copy the UI Kit files if they exist
    kits_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "kits")
    output_kits_dir = os.path.join(output_dir, "kits")

    if os.path.isdir(kits_dir):
        os.makedirs(output_kits_dir, exist_ok=True)

        # Copy the SwitchUIKit
        ui_kit_dir = os.path.join(kits_dir, "SwitchUIKit")
        output_ui_kit_dir = os.path.join(output_kits_dir, "SwitchUIKit")

        if os.path.isdir(ui_kit_dir):
            os.makedirs(output_ui_kit_dir, exist_ok=True)

            # Copy the core UI Kit files
            for file in ["loader.js", "switch-ui-kit.css"]:
                src_path = os.path.join(ui_kit_dir, file)
                dst_path = os.path.join(output_ui_kit_dir, file)

                if os.path.isfile(src_path):
                    shutil.copy2(src_path, dst_path)

            # Copy the component files
            ui_kit_components_dir = os.path.join(ui_kit_dir, "components")
            output_ui_kit_components_dir = os.path.join(output_ui_kit_dir, "components")

            if os.path.isdir(ui_kit_components_dir):
                os.makedirs(output_ui_kit_components_dir, exist_ok=True)

                for file in os.listdir(ui_kit_components_dir):
                    if file.endswith(".js"):
                        src_path = os.path.join(ui_kit_components_dir, file)
                        dst_path = os.path.join(output_ui_kit_components_dir, file)

                        shutil.copy2(src_path, dst_path)

    # Bundle JavaScript and CSS files if requested
    if bundle:
        if verbose:
            print("Bundling files...")

        # Bundle JavaScript files
        if ROLLUP_AVAILABLE:
            _bundle_javascript_files(output_dir, tree_shake, code_splitting, differential_loading, verbose)
        else:
            print("Warning: rollup not installed. Skipping JavaScript bundling.")
            print("Install rollup with: pip install rollup-plugin-python")

        # Bundle CSS files
        _bundle_css_files(output_dir, verbose)

    # Minify JavaScript and CSS files if requested
    if minify:
        if verbose:
            print("Minifying files...")

        # Minify JavaScript files
        if TERSER_AVAILABLE:
            _minify_javascript_files(output_dir, sourcemap, verbose)
        else:
            print("Warning: terser not installed. Skipping JavaScript minification.")
            print("Install terser with: pip install terser")

        # Minify CSS files
        if CSS_COMPRESSOR_AVAILABLE:
            _minify_css_files(output_dir, verbose)
        else:
            print("Warning: csscompressor not installed. Skipping CSS minification.")
            print("Install csscompressor with: pip install csscompressor")

    # Analyze bundle size if requested
    if analyze:
        if verbose:
            print("Analyzing bundle size...")

        _analyze_bundle_size(output_dir)

    if verbose:
        print(f"Build completed successfully: {output_dir}")

    return True

def _bundle_javascript_files(output_dir: str, tree_shake: bool, code_splitting: bool = False, differential_loading: bool = False, verbose: bool = False) -> None:
    """Bundle JavaScript files."""
    # Find all JavaScript files
    js_files = []
    for root, _, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".js") and not file.endswith(".bundle.js") and not file.endswith(".min.js"):
                js_files.append(os.path.join(root, file))

    # Group JavaScript files by directory
    js_files_by_dir = {}
    for js_file in js_files:
        directory = os.path.dirname(js_file)
        if directory not in js_files_by_dir:
            js_files_by_dir[directory] = []
        js_files_by_dir[directory].append(js_file)

    # Bundle JavaScript files by directory
    for directory, files in js_files_by_dir.items():
        # Skip directories with only one file
        if len(files) <= 1:
            continue

        # Create a bundle file
        bundle_file = os.path.join(directory, "bundle.js")

        if verbose:
            print(f"Bundling {len(files)} JavaScript files in {directory} to {bundle_file}")

        # Create a rollup config
        config = {
            "input": files[0],
            "output": {
                "format": "iife",
                "name": "SwitchBundle"
            },
            "plugins": []
        }

        # Configure output based on code splitting
        if code_splitting:
            config["output"]["dir"] = directory
            config["output"]["entryFileNames"] = "[name]-[hash].js"
            config["output"]["chunkFileNames"] = "chunk-[hash].js"
        else:
            config["output"]["file"] = bundle_file

        # Add tree-shaking if requested
        if tree_shake:
            config["treeshake"] = True

        # Add differential loading if requested
        if differential_loading:
            config["plugins"].append({
                "name": "babel",
                "options": {
                    "presets": [
                        ["@babel/preset-env", {
                            "targets": {
                                "browsers": ["last 2 versions", "not dead", "not ie <= 11"]
                            }
                        }]
                    ]
                }
            })

        # Bundle the files
        rollup.rollup(config)

        # Update the HTML file to use the bundle
        html_file = os.path.join(output_dir, "index.html")
        if os.path.isfile(html_file):
            with open(html_file, "r") as f:
                html = f.read()

            # Replace script tags with the bundle
            for js_file in files:
                rel_path = os.path.relpath(js_file, output_dir)
                html = html.replace(f'<script src="{rel_path}"></script>', "")

            # Add the bundle script tag
            if code_splitting:
                # Get the entry file (first chunk)
                entry_files = [f for f in os.listdir(directory) if f.startswith(os.path.basename(files[0]).split('.')[0]) and f.endswith('.js')]
                if entry_files:
                    rel_bundle_path = os.path.relpath(os.path.join(directory, entry_files[0]), output_dir)
                    html = html.replace("</head>", f'<script src="{rel_bundle_path}"></script>\n</head>')
            else:
                rel_bundle_path = os.path.relpath(bundle_file, output_dir)
                html = html.replace("</head>", f'<script src="{rel_bundle_path}"></script>\n</head>')

            # Write the updated HTML
            with open(html_file, "w") as f:
                f.write(html)

def _bundle_css_files(output_dir: str, verbose: bool) -> None:
    """Bundle CSS files."""
    # Find all CSS files
    css_files = []
    for root, _, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".css") and not file.endswith(".bundle.css") and not file.endswith(".min.css"):
                css_files.append(os.path.join(root, file))

    # Group CSS files by directory
    css_files_by_dir = {}
    for css_file in css_files:
        directory = os.path.dirname(css_file)
        if directory not in css_files_by_dir:
            css_files_by_dir[directory] = []
        css_files_by_dir[directory].append(css_file)

    # Bundle CSS files by directory
    for directory, files in css_files_by_dir.items():
        # Skip directories with only one file
        if len(files) <= 1:
            continue

        # Create a bundle file
        bundle_file = os.path.join(directory, "bundle.css")

        if verbose:
            print(f"Bundling {len(files)} CSS files in {directory} to {bundle_file}")

        # Concatenate the files
        with open(bundle_file, "w") as bundle:
            for css_file in files:
                with open(css_file, "r") as f:
                    bundle.write(f.read())
                    bundle.write("\n")

        # Update the HTML file to use the bundle
        html_file = os.path.join(output_dir, "index.html")
        if os.path.isfile(html_file):
            with open(html_file, "r") as f:
                html = f.read()

            # Replace link tags with the bundle
            for css_file in files:
                rel_path = os.path.relpath(css_file, output_dir)
                html = html.replace(f'<link rel="stylesheet" href="{rel_path}">', "")

            # Add the bundle link tag
            rel_bundle_path = os.path.relpath(bundle_file, output_dir)
            html = html.replace("</head>", f'<link rel="stylesheet" href="{rel_bundle_path}">\n</head>')

            # Write the updated HTML
            with open(html_file, "w") as f:
                f.write(html)

def _minify_javascript_files(output_dir: str, sourcemap: bool, verbose: bool) -> None:
    """Minify JavaScript files."""
    # Find all JavaScript files
    for root, _, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".js") and not file.endswith(".min.js"):
                file_path = os.path.join(root, file)

                if verbose:
                    print(f"Minifying {file_path}")

                with open(file_path, "r") as f:
                    content = f.read()

                # Minify the JavaScript
                minified = terser.minify(content, {
                    "compress": True,
                    "mangle": True,
                    "sourceMap": sourcemap
                })

                # Write the minified file
                min_file_path = file_path.replace(".js", ".min.js")
                with open(min_file_path, "w") as f:
                    f.write(minified["code"])

                # Create a source map if requested
                if sourcemap and "map" in minified:
                    with open(f"{min_file_path}.map", "w") as f:
                        f.write(minified["map"])

                # Update the HTML file to use the minified version
                html_file = os.path.join(output_dir, "index.html")
                if os.path.isfile(html_file):
                    with open(html_file, "r") as f:
                        html = f.read()

                    # Replace script tag with the minified version
                    rel_path = os.path.relpath(file_path, output_dir)
                    rel_min_path = os.path.relpath(min_file_path, output_dir)
                    html = html.replace(f'<script src="{rel_path}"></script>', f'<script src="{rel_min_path}"></script>')

                    # Write the updated HTML
                    with open(html_file, "w") as f:
                        f.write(html)

def _minify_css_files(output_dir: str, verbose: bool) -> None:
    """Minify CSS files."""
    # Find all CSS files
    for root, _, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".css") and not file.endswith(".min.css"):
                file_path = os.path.join(root, file)

                if verbose:
                    print(f"Minifying {file_path}")

                with open(file_path, "r") as f:
                    content = f.read()

                # Minify the CSS
                minified = csscompressor.compress(content)

                # Write the minified file
                min_file_path = file_path.replace(".css", ".min.css")
                with open(min_file_path, "w") as f:
                    f.write(minified)

                # Update the HTML file to use the minified version
                html_file = os.path.join(output_dir, "index.html")
                if os.path.isfile(html_file):
                    with open(html_file, "r") as f:
                        html = f.read()

                    # Replace link tag with the minified version
                    rel_path = os.path.relpath(file_path, output_dir)
                    rel_min_path = os.path.relpath(min_file_path, output_dir)
                    html = html.replace(f'<link rel="stylesheet" href="{rel_path}">', f'<link rel="stylesheet" href="{rel_min_path}">')

                    # Write the updated HTML
                    with open(html_file, "w") as f:
                        f.write(html)

def _analyze_bundle_size(output_dir: str) -> None:
    """Analyze bundle size."""
    # Find all JavaScript and CSS files
    js_files = []
    css_files = []
    for root, _, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".js"):
                js_files.append(os.path.join(root, file))
            elif file.endswith(".css"):
                css_files.append(os.path.join(root, file))

    # Calculate total size
    total_js_size = sum(os.path.getsize(file) for file in js_files)
    total_css_size = sum(os.path.getsize(file) for file in css_files)
    total_size = total_js_size + total_css_size

    # Print the analysis
    print("\nBundle Size Analysis:")
    print(f"Total JavaScript size: {_format_size(total_js_size)}")
    print(f"Total CSS size: {_format_size(total_css_size)}")
    print(f"Total bundle size: {_format_size(total_size)}")

    # Print the largest files
    print("\nLargest JavaScript files:")
    js_files.sort(key=os.path.getsize, reverse=True)
    for i, file in enumerate(js_files[:5]):
        print(f"{i+1}. {os.path.relpath(file, output_dir)}: {_format_size(os.path.getsize(file))}")

    print("\nLargest CSS files:")
    css_files.sort(key=os.path.getsize, reverse=True)
    for i, file in enumerate(css_files[:5]):
        print(f"{i+1}. {os.path.relpath(file, output_dir)}: {_format_size(os.path.getsize(file))}")

def _format_size(size_in_bytes: int) -> str:
    """Format a size in bytes to a human-readable string."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.2f} KB"
    else:
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"
