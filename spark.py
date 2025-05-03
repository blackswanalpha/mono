#!/usr/bin/env python3
"""
Launcher for Spark Editor
"""

import sys
import os
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main module
from spark.main import main

if __name__ == "__main__":
    main()
