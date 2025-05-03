#!/usr/bin/env python3
"""
Run script for Spark Editor
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import the main module
from spark.main import main

if __name__ == "__main__":
    main()
