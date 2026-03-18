import subprocess
import os
import time

IPTABLES_RULES_DIR = '/tmp/hotspot_rules/'
IPTABLES_RULES_LOG = '/tmp/hotspot_rules.log'

def ensure_rules_dir():
    """Ensure the rules directory exists"""
    os.makedirs(IPTABLES_RULES_DIR, exist_ok=True)

def apply_firewall_rule(user_ip, duration_minutes):
    """
    Apply iptables rule to allow internet access for a specific IP.
    Rules are stored with a comment for tracking.
    """
    try:
        ensure_rules_dir()
        
        # Mark this IP as allowed
        rule_file = os.path.join(IPTABLES_RULES_DIR, f'{user_ip}.rule')
        with open(rule_file, 'w') as f:
            f.write(f'EXPIRED_AT={int(time.time()) + (duration_minutes * 60)}\n')
        
        # Apply iptables rule - allow traffic from user IP
        cmd = [
            'sudo', 'iptables', '-A', 'FORWARD',
            '-s', user_ip, '-j', 'ACCEPT',
            '-m', 'comment', '--comment', f'hotspot_{user_ip}'
        ]
        
        # Would execute with proper permissions in real deployment
        # subprocess.run(cmd, check=True)
        
        with open(IPTABLES_RULES_LOG, 'a') as f:
            f.write(f'ALLOW {user_ip} for {duration_minutes} minutes\n')
    
    except Exception as e:
        print(f'Error applying firewall rule for {user_ip}: {str(e)}')

def remove_firewall_rule(user_ip):
    """Remove iptables rule for a specific IP"""
    try:
        # Remove rule file
        rule_file = os.path.join(IPTABLES_RULES_DIR, f'{user_ip}.rule')
        if os.path.exists(rule_file):
            os.remove(rule_file)
        
        # Remove iptables rule
        cmd = [
            'sudo', 'iptables', '-D', 'FORWARD',
            '-s', user_ip, '-j', 'ACCEPT',
            '-m', 'comment', '--comment', f'hotspot_{user_ip}'
        ]
        
        # Would execute with proper permissions in real deployment
        # subprocess.run(cmd, check=True)
        
        with open(IPTABLES_RULES_LOG, 'a') as f:
            f.write(f'REVOKE {user_ip}\n')
    
    except Exception as e:
        print(f'Error removing firewall rule for {user_ip}: {str(e)}')

def check_ip_allowed(user_ip):
    """Check if an IP is in the allowed list"""
    rule_file = os.path.join(IPTABLES_RULES_DIR, f'{user_ip}.rule')
    return os.path.exists(rule_file)
