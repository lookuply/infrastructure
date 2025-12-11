#!/bin/bash
# Lookuply Monitor - Run Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run monitor
echo "Starting Lookuply Monitor..."
echo "Press Ctrl+C to quit"
echo ""

# Check if we need sudo for log access
if [ ! -r /var/log/nginx/access.log ]; then
    echo "Note: Running with sudo for log file access"
    sudo -E venv/bin/python3 lookuply-monitor.py
else
    python3 lookuply-monitor.py
fi
