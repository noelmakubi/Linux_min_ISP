    # Hotspot Billing System Configuration

import os

# Flask Configuration
DEBUG = True
SECRET_KEY = 'your-secret-key-change-this'

# Database Configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///hotspot_billing.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Network Configuration
INTERFACE_CLIENT = 'eth0'  # Interface connected to upstream WiFi
INTERFACE_AP = 'wlan1'    # Virtual interface for hotspot AP
AP_SSID = 'FreeHotspot'
AP_CHANNEL = 6
AP_GATEWAY = '192.168.10.1'
AP_NETMASK = '255.255.255.0'
AP_SUBNET = '192.168.10.0/24'
DHCP_RANGE_START = '192.168.10.10'
DHCP_RANGE_END = '192.168.10.120'


# Captive Portal Configuration
PORTAL_PORT = 8080
PORTAL_REDIRECT_PORT = 8080

# Admin Panel Configuration
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'  # CHANGE THIS!

# Auto-Expiry Configuration
EXPIRY_CHECK_INTERVAL = 30  # seconds

# System Paths
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'hotspot_billing.db')
LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs')
IPTABLES_RULES_PATH = '/tmp/hotspot_rules/'
