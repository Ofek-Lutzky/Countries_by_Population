#!/usr/bin/env python3
"""
Entry point script for the Wikipedia Countries Population Scraper.

This script allows running the application without module path issues.
"""

import sys
import os

# Add the current directory to Python path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import and run the main function
from src.presentation.cli.main import main

if __name__ == "__main__":
    main()