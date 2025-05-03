"""
Mono Utils - Utility functions for the Mono language
"""

import os
import sys

def get_mono_root():
    """
    Get the root directory of the Mono installation.
    """
    # If MONO_ROOT environment variable is set, use it
    if 'MONO_ROOT' in os.environ:
        return os.environ['MONO_ROOT']

    # Otherwise, use the directory containing this file
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_templates_dir():
    """
    Get the templates directory.
    """
    return os.path.join(get_mono_root(), 'templates')

def get_lib_dir():
    """
    Get the lib directory.
    """
    return os.path.join(get_mono_root(), 'lib')

def get_bin_dir():
    """
    Get the bin directory.
    """
    return os.path.join(get_mono_root(), 'bin')

def is_mono_file(file_path):
    """
    Check if a file is a Mono script.
    """
    return file_path.endswith('.mono')

def find_mono_file(file_name):
    """
    Find a Mono script file.
    """
    # If the file exists as is, return it
    if os.path.isfile(file_name):
        return file_name

    # If the file doesn't have a .mono extension, try adding it
    if not file_name.endswith('.mono'):
        file_with_ext = file_name + '.mono'
        if os.path.isfile(file_with_ext):
            return file_with_ext

    # Check in the templates directory
    templates_dir = get_templates_dir()
    template_path = os.path.join(templates_dir, file_name)
    if os.path.isfile(template_path):
        return template_path

    # Check in the templates directory with .mono extension
    if not file_name.endswith('.mono'):
        template_path_with_ext = os.path.join(templates_dir, file_with_ext)
        if os.path.isfile(template_path_with_ext):
            return template_path_with_ext

    # File not found
    return None

def print_error(message):
    """
    Print an error message.
    """
    print(f"Error: {message}", file=sys.stderr)

def print_warning(message):
    """
    Print a warning message.
    """
    print(f"Warning: {message}", file=sys.stderr)

def print_info(message):
    """
    Print an info message.
    """
    print(message)

def print_usage():
    """
    Print usage information.
    """
    print("Usage: mono [options] <script.mono>")
    print("")
    print("Options:")
    print("  -h, --help       Show this help message and exit")
    print("  -v, --version    Show version information and exit")
    print("  -r, --reactive   Use the reactive Mono interpreter")
    print("  -t, --type-check Enable static type checking")
    print("  -l, --lifecycle  Enable component lifecycle hooks")
    print("  -a, --arithmetic Enable complex arithmetic operations")
    print("  -c, --collections Enable arrays, dictionaries, and boolean operations")
    print("  -p, --concurrent Enable concurrency and parallelism features")
    print("  -e, --elements   Enable component elements support")
    print("  -f, --frames     Enable frames support")
    print("  --verbose        Show detailed information during execution")
    print("")
    print("Examples:")
    print("  mono templates/start.mono")
    print("  mono -r templates/reactive_app.mono")
    print("  mono -t templates/typed_counter.mono")
    print("  mono -l templates/lifecycle_demo.mono")
    print("  mono -a templates/arithmetic_demo.mono")
    print("  mono -c templates/collections_demo.mono")
    print("  mono -p templates/concurrent_demo.mono")
    print("  mono -e templates/element_demo.mono")
    print("  mono -f templates/frames_demo.mono")

def print_version():
    """
    Print version information.
    """
    print("Mono Language Interpreter v1.0.0")
    print("Copyright (c) 2023 Mono Team")
    print("License: MIT")

def parse_args(args):
    """
    Parse command-line arguments.
    """
    options = {
        'help': False,
        'version': False,
        'reactive': False,
        'type_check': False,
        'lifecycle': False,
        'arithmetic': False,
        'collections': False,
        'concurrent': False,
        'elements': False,
        'frames': False,
        'verbose': False,
        'script': None
    }

    i = 0
    while i < len(args):
        arg = args[i]

        if arg in ('-h', '--help'):
            options['help'] = True
        elif arg in ('-v', '--version'):
            options['version'] = True
        elif arg in ('-r', '--reactive'):
            options['reactive'] = True
        elif arg in ('-t', '--type-check'):
            options['type_check'] = True
        elif arg in ('-l', '--lifecycle'):
            options['lifecycle'] = True
        elif arg in ('-a', '--arithmetic'):
            options['arithmetic'] = True
        elif arg in ('-c', '--collections'):
            options['collections'] = True
        elif arg in ('-p', '--concurrent'):
            options['concurrent'] = True
        elif arg in ('-e', '--elements'):
            options['elements'] = True
        elif arg in ('-f', '--frames'):
            options['frames'] = True
        elif arg in ('--verbose'):
            options['verbose'] = True
        elif not arg.startswith('-'):
            options['script'] = arg
        else:
            print_error(f"Unknown option: {arg}")
            options['help'] = True

        i += 1

    return options
