#!/usr/bin/env bash

# Hotspot Billing System - Admin Panel Launcher
# This script activates the virtual environment and opens the admin panel

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the hotspot_billing_system directory
cd "$SCRIPT_DIR" || exit 1

echo "🔧 Starting Hotspot Billing System Admin Panel..."
echo ""

# Activate virtual environment (located in parent directory)
if [ -d "../venv" ]; then
    source ../venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found at: $SCRIPT_DIR/../venv"
    echo "Please ensure the venv folder exists in the parent directory"
    exit 1
fi

# Check if Flask app is already running on port 8080
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "✅ Flask app already running on port 8080"
else
    echo "🚀 Starting Flask server..."
    # Start Flask in background
    python3 run.py > /dev/null 2>&1 &
    FLASK_PID=$!
    echo "✅ Flask server started (PID: $FLASK_PID)"
    
    # Wait a moment for server to start
    sleep 3
fi

echo ""
echo "🌐 Opening Admin Panel in Firefox..."
echo "   URL: http://127.0.0.1:8080/admin"
echo ""
echo "💡 Default credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""

# Open Firefox with admin panel
firefox http://127.0.0.1:8080/admin &

echo "✨ Done! You can now manage your hotspot."
echo "   Press Ctrl+C to stop the Flask server when done"

# Keep the terminal open and wait
wait
