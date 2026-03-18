from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app import db
from app.models import Voucher, Session, Log
from datetime import datetime, timedelta
from app.utils.firewall import apply_firewall_rule, remove_firewall_rule
import os

portal_bp = Blueprint('portal', __name__)

@portal_bp.route('/')
def index():
    """Captive portal login page"""
    return render_template('login.html')

@portal_bp.route('/login', methods=['POST'])
def login():
    """Validate voucher and grant access"""
    try:
        data = request.get_json()
        voucher_code = data.get('voucher_code', '').strip().upper()
        user_ip = request.remote_addr
        
        # Find voucher
        voucher = Voucher.query.filter_by(code=voucher_code).first()
        
        if not voucher:
            return jsonify({'success': False, 'message': 'Invalid voucher code'}), 400
        
        if voucher.status != 'unused':
            return jsonify({'success': False, 'message': 'Voucher already used or disabled'}), 400
        
        # Calculate expiry time
        start_time = datetime.utcnow()
        expiry_time = start_time + timedelta(minutes=voucher.allowed_minutes)
        
        # Create session
        session = Session(
            voucher_id=voucher.id,
            user_ip=user_ip,
            user_mac=request.remote_addr,  # Would need MAC from client in real implementation
            start_time=start_time,
            expiry_time=expiry_time
        )
        
        db.session.add(session)
        db.session.commit()
        
        # Mark voucher as used
        voucher.status = 'used'
        voucher.used_at = start_time
        db.session.commit()
        
        # Apply firewall rules to allow internet access for this IP
        apply_firewall_rule(user_ip, voucher.allowed_minutes)
        
        # Log login
        log_entry = Log(
            session_id=session.id,
            event_type='login',
            user_ip=user_ip,
            details=f'Voucher: {voucher_code}, Duration: {voucher.allowed_minutes} minutes'
        )
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Access granted for {voucher.allowed_minutes} minutes',
            'expiry_time': expiry_time.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@portal_bp.route('/status')
def status():
    """Check if user has active session"""
    user_ip = request.remote_addr
    session = Session.query.filter_by(user_ip=user_ip, is_active=True).first()
    
    if session:
        time_remaining = (session.expiry_time - datetime.utcnow()).total_seconds()
        return jsonify({
            'authenticated': True,
            'time_remaining_seconds': max(0, int(time_remaining))
        })
    
    return jsonify({'authenticated': False})

@portal_bp.route('/logout', methods=['POST'])
def logout():
    """Manually end user session"""
    user_ip = request.remote_addr
    session = Session.query.filter_by(user_ip=user_ip, is_active=True).first()
    
    if session:
        session.is_active = False
        session.end_time = datetime.utcnow()
        db.session.commit()
        
        # Remove firewall rules
        remove_firewall_rule(user_ip)
        
        log_entry = Log(
            session_id=session.id,
            event_type='manual_disconnect',
            user_ip=user_ip
        )
        db.session.add(log_entry)
        db.session.commit()
    
    return jsonify({'success': True})
