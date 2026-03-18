#!/usr/bin/env python3
"""
Main Flask application entry point for Hotspot Billing System
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

app = create_app()

if __name__ == '__main__':
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Initialize database
    with app.app_context():
        db.create_all()
    
    # Run development server
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True,
        use_reloader=True
    )
