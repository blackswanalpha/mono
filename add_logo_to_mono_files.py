#!/usr/bin/env python3

import os
import glob

# ASCII art logo for Mono
MONO_LOGO_ASCII = """
//  __  __
// |  \/  | ___  _ __   ___
// | |\/| |/ _ \| '_ \ / _ \
// | |  | | (_) | | | | (_) |
// |_|  |_|\___/|_| |_|\___/
//
// Mono Language - A component-based language with reactive programming and static typing
"""

def add_logo_to_file(file_path):
    """Add the Mono logo to a .mono file if it doesn't already have it."""
    with open(file_path, 'r') as f:
        content = f.read()

    # Check if the logo is already in the file
    if "// Mono Language" in content:
        print(f"Logo already exists in {file_path}")
        return

    # Add the logo at the beginning of the file
    with open(file_path, 'w') as f:
        f.write(MONO_LOGO_ASCII + "\n" + content)

    print(f"Added logo to {file_path}")

def main():
    """Find all .mono files and add the logo to them."""
    # Find all .mono files in the templates directory
    mono_files = glob.glob("templates/*.mono")

    # Add these specific files that we know about
    additional_files = [
        "templates/typed_counter.mono",
        "templates/generic_list.mono",
        "templates/reactive_app.mono",
        "templates/simple_todo.mono",
        "templates/simple_reactive.mono",
        "templates/basic_counter.mono",
        "templates/start.mono",
        "templates/counter_test.mono",
        "templates/calculator.mono"
    ]

    # Add additional files if they exist
    for file_path in additional_files:
        if os.path.exists(file_path):
            mono_files.append(file_path)

    # Process all files
    for file_path in mono_files:
        add_logo_to_file(file_path)

    print(f"Processed {len(mono_files)} .mono files")

if __name__ == "__main__":
    main()
