#!/usr/bin/env python3
"""
Auto-expiry daemon for Hotspot Billing System

Runs periodically to check for expired sessions and revoke access.
Should be run as a background service or cron job.
"""

import os
import sys
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Session, Log
from app.utils.firewall import remove_firewall_rule

app = create_app()

def check_and_expire_sessions():
    """Check all active sessions and expire them if time has passed"""
    with app.app_context():
        current_time = datetime.utcnow()
        
        # Find all expired active sessions
        expired_sessions = Session.query.filter(
            Session.is_active == True,
            Session.expiry_time <= current_time
        ).all()
        
        for session in expired_sessions:
            try:
                # Mark session as inactive
                session.is_active = False
                session.end_time = current_time
                db.session.commit()
                
                # Remove firewall rules
                remove_firewall_rule(session.user_ip)
                
                # Log the expiry
                log_entry = Log(
                    session_id=session.id,
                    event_type='auto_expired',
                    user_ip=session.user_ip,
                    details=f'Session expired after {session.voucher.allowed_minutes} minutes'
                )
                db.session.add(log_entry)
                db.session.commit()
                
                print(f'[{current_time.isoformat()}] Session expired for IP: {session.user_ip}')
                
            except Exception as e:
                print(f'[{current_time.isoformat()}] Error expiring session {session.id}: {str(e)}')
                db.session.rollback()

def main():
    """Main loop for auto-expiry daemon"""
    from config.settings import EXPIRY_CHECK_INTERVAL
    
    print(f'[{datetime.utcnow().isoformat()}] Starting hotspot auto-expiry daemon...')
    print(f'Checking for expired sessions every {EXPIRY_CHECK_INTERVAL} seconds')
    
    try:
        while True:
            check_and_expire_sessions()
            time.sleep(EXPIRY_CHECK_INTERVAL)
    except KeyboardInterrupt:
        print(f'\n[{datetime.utcnow().isoformat()}] Shutting down auto-expiry daemon')
        sys.exit(0)
    except Exception as e:
        print(f'[{datetime.utcnow().isoformat()}] Fatal error in auto-expiry daemon: {str(e)}')
        sys.exit(1)

if __name__ == '__main__':
    main()
