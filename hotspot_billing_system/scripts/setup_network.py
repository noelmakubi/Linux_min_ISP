#!/usr/bin/env python3
"""
Network setup script for Hotspot Billing System

This script configures:
1. IP forwarding
2. NAT rules
3. HTTP redirect to captive portal
4. DHCP server settings

Run this script with: sudo python3 setup_network.py

Note: This script assumes you have hostapd, dnsmasq installed and configured.
"""

import subprocess
import os
import sys
import config.settings as settings

# Configuration
INTERFACE_CLIENT = settings.INTERFACE_CLIENT  # Interface connected to upstream WiFi
INTERFACE_AP = settings.INTERFACE_AP        # Virtual AP interface
AP_GATEWAY = settings.AP_GATEWAY
AP_NETMASK = settings.AP_NETMASK
AP_SUBNET = settings.AP_SUBNET
PORTAL_PORT = settings.PORTAL_PORT

def run_command(cmd, description):
    """Run a shell command with error handling"""
    print(f'\n► {description}')
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f'  ✓ {description} - Success')
        return True
    except subprocess.CalledProcessError as e:
        print(f'  ✗ {description} - Failed')
        print(f'  Error: {e.stderr}')
        return False

def setup_ip_forwarding():
    """Enable IP forwarding on the system"""
    commands = [
        ('echo 1 > /proc/sys/net/ipv4/ip_forward', 'Enabling IP forwarding'),
        ('sysctl -w net.ipv4.ip_forward=1', 'Setting sysctl ip_forward'),
    ]
    
    for cmd, desc in commands:
        if not run_command(f'sudo bash -c "{cmd}"', desc):
            return False
    return True

def setup_nat_rules():
    """Configure NAT rules for internet access"""
    commands = [
        (f'sudo iptables -t nat -A POSTROUTING -o {INTERFACE_AP} -j MASQUERADE', 'Adding MASQUERADE rule'),
        (f'sudo iptables -A FORWARD -i {INTERFACE_AP} -o {INTERFACE_CLIENT} -m state --state RELATED,ESTABLISHED -j ACCEPT', 'Allow inbound forwarding'),
        (f'sudo iptables -A FORWARD -i {INTERFACE_CLIENT} -o {INTERFACE_AP} -j ACCEPT', 'Allow outbound forwarding'),
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    return True

def setup_dns_redirect():
    """Redirect HTTP requests to captive portal"""
    commands = [
        (f'sudo iptables -t nat -A PREROUTING -i {INTERFACE_AP} -p tcp --dport 80 -j REDIRECT --to-port {PORTAL_PORT}', 
         'Redirect HTTP traffic to portal'),
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    return True

def setup_ip_address():
    """Configure AP interface IP address"""
    commands = [
        (f'sudo ip addr add {AP_GATEWAY}/24 dev {INTERFACE_AP}', 
         f'Setting AP interface IP to {AP_GATEWAY}'),
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    return True

def main():
    """Main setup routine"""
    print('═' * 60)
    print('Hotspot Billing System - Network Setup')
    print('═' * 60)
    
    # Check if running as root
    if os.geteuid() != 0:
        print('ERROR: This script must be run as root (use: sudo python3 setup_network.py)')
        sys.exit(1)
    
    print('\nConfiguring network interfaces and firewall rules...')
    
    steps = [
        ('IP Forwarding', setup_ip_forwarding),
        ('NAT Rules', setup_nat_rules),
        ('DNS Redirect', setup_dns_redirect),
        ('IP Address', setup_ip_address),
    ]
    
    completed = 0
    for step_name, step_func in steps:
        if step_func():
            completed += 1
        else:
            print(f'\nWarning: {step_name} setup encountered issues')
    
    print('\n' + '═' * 60)
    print(f'✓ Network setup completed: {completed}/{len(steps)} steps successful')
    print('═' * 60)
    print('\nNext steps:')
    print('1. Ensure hostapd is configured and running')
    print('2. Ensure dnsmasq is configured and running')
    print('3. Start the Flask app: python3 run.py')
    print('4. Start the auto-expiry daemon: python3 scripts/auto_expiry.py')

if __name__ == '__main__':
    main()
