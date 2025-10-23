#!/usr/bin/env python3
"""
Startup script for the Flask API backend
"""
import os
import sys

def main():
    # Change to the API directory
    api_dir = os.path.join(os.path.dirname(__file__), 'api')
    os.chdir(api_dir)

    # Run the Flask app
    os.system('python app.py')

if __name__ == '__main__':
    main()