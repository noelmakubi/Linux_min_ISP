from flask import Blueprint, render_template, request, jsonify, session as flask_session
from flask_sqlalchemy import SQLAlchemy
from app import db
from app.models import Voucher, Session, Log
from datetime import datetime, timedelta
from functools import wraps
import secrets
import string

admin_bp = Blueprint('admin', __name__)

# Simple auth decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in flask_session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
def admin_index():
    """Admin login page"""
    return render_template('admin_login.html')

@admin_bp.route('/login', methods=['POST'])
def login():
    """Admin login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Simple hardcoded auth (should use proper auth in production)
        from config.settings import ADMIN_USERNAME, ADMIN_PASSWORD
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            flask_session['admin_logged_in'] = True
            flask_session['username'] = username
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard page"""
    return render_template('admin_dashboard.html')

@admin_bp.route('/api/stats')
@admin_required
def get_stats():
    """Get system statistics"""
    try:
        active_sessions = Session.query.filter_by(is_active=True).count()
        total_vouchers = Voucher.query.count()
        used_vouchers = Voucher.query.filter_by(status='used').count()
        unused_vouchers = Voucher.query.filter_by(status='unused').count()
        
        return jsonify({
            'active_sessions': active_sessions,
            'total_vouchers': total_vouchers,
            'used_vouchers': used_vouchers,
            'unused_vouchers': unused_vouchers
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/vouchers', methods=['GET'])
@admin_required
def get_vouchers():
    """List all vouchers"""
    try:
        page = request.args.get('page', 1, type=int)
        vouchers = Voucher.query.paginate(page=page, per_page=20)
        
        return jsonify({
            'vouchers': [
                {
                    'id': v.id,
                    'code': v.code,
                    'allowed_minutes': v.allowed_minutes,
                    'status': v.status,
                    'created_at': v.created_at.isoformat(),
                    'used_at': v.used_at.isoformat() if v.used_at else None
                }
                for v in vouchers.items
            ],
            'total': vouchers.total,
            'pages': vouchers.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/vouchers', methods=['POST'])
@admin_required
def create_voucher():
    """Create new vouchers"""
    try:
        data = request.get_json()
        count = data.get('count', 1)
        allowed_minutes = data.get('allowed_minutes', 60)
        
        vouchers = []
        for _ in range(count):
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))
            voucher = Voucher(code=code, allowed_minutes=allowed_minutes, status='unused')
            db.session.add(voucher)
            vouchers.append({'code': code, 'allowed_minutes': allowed_minutes})
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'vouchers': vouchers,
            'message': f'Created {count} voucher(s)'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/sessions')
@admin_required
def get_sessions():
    """List all active sessions"""
    try:
        sessions = Session.query.filter_by(is_active=True).all()
        
        return jsonify({
            'sessions': [
                {
                    'id': s.id,
                    'user_ip': s.user_ip,
                    'user_mac': s.user_mac,
                    'start_time': s.start_time.isoformat(),
                    'expiry_time': s.expiry_time.isoformat(),
                    'time_remaining': int((s.expiry_time - datetime.utcnow()).total_seconds())
                }
                for s in sessions
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/sessions/<int:session_id>/disconnect', methods=['POST'])
@admin_required
def disconnect_session(session_id):
    """Manually disconnect a user"""
    try:
        from app.utils.firewall import remove_firewall_rule
        
        session_obj = Session.query.get(session_id)
        if not session_obj:
            return jsonify({'error': 'Session not found'}), 404
        
        session_obj.is_active = False
        session_obj.end_time = datetime.utcnow()
        db.session.commit()
        
        # Remove firewall rules
        remove_firewall_rule(session_obj.user_ip)
        
        log_entry = Log(
            session_id=session_id,
            event_type='admin_disconnect',
            user_ip=session_obj.user_ip
        )
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/logs')
@admin_required
def get_logs():
    """Get system logs"""
    try:
        page = request.args.get('page', 1, type=int)
        logs = Log.query.order_by(Log.timestamp.desc()).paginate(page=page, per_page=50)
        
        return jsonify({
            'logs': [
                {
                    'id': l.id,
                    'event_type': l.event_type,
                    'user_ip': l.user_ip,
                    'details': l.details,
                    'timestamp': l.timestamp.isoformat()
                }
                for l in logs.items
            ],
            'total': logs.total,
            'pages': logs.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/logout', methods=['POST'])
def logout():
    """Admin logout"""
    flask_session.clear()
    return jsonify({'success': True})
