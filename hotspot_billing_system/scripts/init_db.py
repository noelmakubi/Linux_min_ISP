#!/usr/bin/env python3
"""
Initialize database with sample data for Hotspot Billing System
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Voucher
import secrets
import string

app = create_app()

def create_sample_vouchers(count=10):
    """Create sample vouchers for testing"""
    with app.app_context():
        # Clear existing vouchers (for demo purposes)
        Voucher.query.delete()
        db.session.commit()
        
        print(f'Creating {count} sample vouchers...\n')
        
        vouchers = []
        for i in range(count):
            # Generate random voucher code
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))
            
            voucher = Voucher(
                code=code,
                allowed_minutes=60,
                status='unused',
                user_info=f'Sample Voucher {i+1}'
            )
            vouchers.append(voucher)
            db.session.add(voucher)
            print(f'  {i+1}. {code} - 60 minutes')
        
        db.session.commit()
        
        print(f'\n✓ Created {count} sample vouchers')
        print('\nVoucher codes (save these for testing):')
        for v in vouchers:
            print(f'  {v.code}')

if __name__ == '__main__':
    create_sample_vouchers()
