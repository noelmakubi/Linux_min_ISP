#!/bin/bash

# Quick installation script for Hotspot Billing System
# Run with: bash install.sh

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Hotspot Billing System - Installation Script            ║"
echo "╚════════════════════════════════════════════════════════════╝"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo "❌ This script must be run as root"
    echo "   Run: sudo bash install.sh"
    exit 1
fi

INSTALL_DIR="/home/noel/Desktop/sideAPP/hotspot_billing_system"

echo ""
echo "📦 Installing system dependencies..."
apt-get update
apt-get install -y python3-pip hostapd dnsmasq iptables sqlite3 git

echo ""
echo "📚 Installing Python dependencies..."
pip3 install -r "$INSTALL_DIR/requirements.txt"

echo ""
echo "🔧 Setting up permissions..."
chmod +x "$INSTALL_DIR/run.py"
chmod +x "$INSTALL_DIR/scripts/auto_expiry.py"
chmod +x "$INSTALL_DIR/scripts/setup_network.py"
chmod +x "$INSTALL_DIR/scripts/init_db.py"

echo ""
echo "📋 Creating logs directory..."
mkdir -p "$INSTALL_DIR/logs"

echo ""
echo "💾 Initializing database..."
cd "$INSTALL_DIR"
python3 scripts/init_db.py

echo ""
echo "✅ Installation Complete!"
echo ""
echo "Next steps:"
echo "1. Review configuration: nano $INSTALL_DIR/config/settings.py"
echo "2. Setup network: sudo python3 $INSTALL_DIR/scripts/setup_network.py"
echo "3. Start application: python3 $INSTALL_DIR/run.py"
echo "4. Start expiry daemon: python3 $INSTALL_DIR/scripts/auto_expiry.py"
echo ""
echo "Admin Panel: http://192.168.10.1:8080/admin"
echo "Portal: http://192.168.10.1:8080"
