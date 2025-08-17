#!/usr/bin/env python3
"""
Entry point script for deployment
This script ensures the application starts correctly in deployment environments
"""

import os
import sys

# Ensure the current directory is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main application
from main import main

if __name__ == "__main__":
    main()