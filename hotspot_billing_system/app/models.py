from app import db
from datetime import datetime

class Voucher(db.Model):
    __tablename__ = 'vouchers'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    allowed_minutes = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='unused')  # unused, used, disabled
    user_info = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Voucher {self.code}>'


class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    voucher_id = db.Column(db.Integer, db.ForeignKey('vouchers.id'), nullable=False)
    user_ip = db.Column(db.String(15), nullable=False, index=True)
    user_mac = db.Column(db.String(17), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_time = db.Column(db.DateTime, nullable=False)
    bandwidth_limit_mbps = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    end_time = db.Column(db.DateTime, nullable=True)
    
    voucher = db.relationship('Voucher', backref='sessions')
    
    def __repr__(self):
        return f'<Session {self.user_ip} {self.start_time}>'


class Log(db.Model):
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=True)
    event_type = db.Column(db.String(50), nullable=False)  # login, expired, manual_disconnect, etc
    user_ip = db.Column(db.String(15), nullable=False)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Log {self.event_type} {self.timestamp}>'
