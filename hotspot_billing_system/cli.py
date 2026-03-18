#!/usr/bin/env python3
"""
Command-line utility for managing Hotspot Billing System

Usage:
  python3 cli.py vouchers list
  python3 cli.py vouchers create --count 10 --duration 60
  python3 cli.py sessions list
  python3 cli.py sessions disconnect <session_id>
  python3 cli.py admin create-admin --username admin --password newpass
"""

import sys
import argparse
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Voucher, Session, Log
from datetime import datetime
import secrets
import string

app = create_app()

def format_table(headers, rows):
    """Format data as a simple table"""
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Print header
    header_line = ' | '.join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    print(header_line)
    print('-' * len(header_line))
    
    # Print rows
    for row in rows:
        print(' | '.join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)))

def vouchers_list():
    """List all vouchers"""
    with app.app_context():
        vouchers = Voucher.query.all()
        if not vouchers:
            print("No vouchers found")
            return
        
        headers = ['ID', 'Code', 'Duration', 'Status', 'Created', 'Used']
        rows = []
        for v in vouchers:
            rows.append([
                v.id,
                v.code,
                f'{v.allowed_minutes}m',
                v.status,
                v.created_at.strftime('%Y-%m-%d %H:%M'),
                v.used_at.strftime('%Y-%m-%d %H:%M') if v.used_at else '-'
            ])
        format_table(headers, rows)

def vouchers_create(count, duration):
    """Create new vouchers"""
    with app.app_context():
        vouchers = []
        for _ in range(count):
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))
            voucher = Voucher(code=code, allowed_minutes=duration, status='unused')
            db.session.add(voucher)
            vouchers.append(code)
        
        db.session.commit()
        print(f'✓ Created {count} vouchers for {duration} minutes\n')
        
        for code in vouchers:
            print(code)

def sessions_list():
    """List active sessions"""
    with app.app_context():
        sessions = Session.query.filter_by(is_active=True).all()
        if not sessions:
            print("No active sessions")
            return
        
        headers = ['ID', 'IP', 'Start', 'Expiry', 'Duration']
        rows = []
        for s in sessions:
            remaining = (s.expiry_time - datetime.utcnow()).total_seconds()
            mins = int(remaining / 60)
            rows.append([
                s.id,
                s.user_ip,
                s.start_time.strftime('%H:%M:%S'),
                s.expiry_time.strftime('%H:%M:%S'),
                f'{mins}m'
            ])
        format_table(headers, rows)

def sessions_disconnect(session_id):
    """Disconnect a session"""
    with app.app_context():
        session = Session.query.get(session_id)
        if not session:
            print(f"Session {session_id} not found")
            return
        
        session.is_active = False
        session.end_time = datetime.utcnow()
        db.session.commit()
        print(f"✓ Disconnected session {session_id}")

def main():
    parser = argparse.ArgumentParser(description='Hotspot Billing System CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Vouchers
    vouchers_parser = subparsers.add_parser('vouchers', help='Manage vouchers')
    vouchers_subparsers = vouchers_parser.add_subparsers(dest='action')
    
    vouchers_subparsers.add_parser('list', help='List all vouchers')
    
    create_parser = vouchers_subparsers.add_parser('create', help='Create vouchers')
    create_parser.add_argument('--count', type=int, default=1, help='Number of vouchers')
    create_parser.add_argument('--duration', type=int, default=60, help='Duration in minutes')
    
    # Sessions
    sessions_parser = subparsers.add_parser('sessions', help='Manage sessions')
    sessions_subparsers = sessions_parser.add_subparsers(dest='action')
    
    sessions_subparsers.add_parser('list', help='List active sessions')
    
    disconnect_parser = sessions_subparsers.add_parser('disconnect', help='Disconnect a session')
    disconnect_parser.add_argument('session_id', type=int, help='Session ID')
    
    args = parser.parse_args()
    
    if args.command == 'vouchers':
        if args.action == 'list':
            vouchers_list()
        elif args.action == 'create':
            vouchers_create(args.count, args.duration)
    elif args.command == 'sessions':
        if args.action == 'list':
            sessions_list()
        elif args.action == 'disconnect':
            sessions_disconnect(args.session_id)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
