"""
run_collector.py — Entry point for the data collector.
Run from the project root: python run_collector.py
"""
import sys
import os

# Ensure project root is on the path so all imports resolve correctly
sys.path.insert(0, os.path.dirname(__file__))

# Load .env first before other imports access os.getenv
import config

from collector.collector import run_collector

if __name__ == "__main__":
    run_collector()
