"""
Pytest configuration and fixtures for testing
"""

import pytest
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
