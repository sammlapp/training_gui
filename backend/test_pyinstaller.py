#!/usr/bin/env python3
"""
Simple test script to verify PyInstaller packaging works
"""
import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description='Test PyInstaller packaging')
    parser.add_argument('--test', action='store_true', help='Run basic test')
    args = parser.parse_args()
    
    if args.test:
        print("PyInstaller test successful!")
        print(f"Python version: {sys.version}")
        print(f"Running from: {os.path.dirname(os.path.abspath(__file__))}")
        return 0
    else:
        print("Usage: test_pyinstaller --test")
        return 1

if __name__ == "__main__":
    sys.exit(main())