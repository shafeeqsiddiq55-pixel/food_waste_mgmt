# ============================================================
# utils/helpers.py - Utility Functions
# ============================================================

from functools import wraps
from flask import session, redirect, url_for, flash
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================================
# AUTH DECORATORS
# ============================================================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get('role') not in roles:
                flash('Access denied. Insufficient permissions.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated
    return decorator

# ============================================================
# NOTIFICATION HELPER
# ============================================================
def send_notification(cur, user_id, title, message, ntype='info',
                      donation_id=None, request_id=None):
    """Insert a notification record into the database."""
    cur.execute("""
        INSERT INTO notifications (user_id, title, message, type, related_donation_id, related_request_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_id, title, message, ntype, donation_id, request_id))

# ============================================================
# TIME HELPERS
# ============================================================
def time_until_expiry(expiry_time):
    """Return human-readable time until expiry."""
    from datetime import datetime
    now = datetime.now()
    if not expiry_time:
        return 'Unknown'
    delta = expiry_time - now
    if delta.total_seconds() < 0:
        return 'Expired'
    hours = int(delta.total_seconds() // 3600)
    minutes = int((delta.total_seconds() % 3600) // 60)
    if hours > 0:
        return f'{hours}h {minutes}m'
    return f'{minutes} minutes'

def is_expiring_soon(expiry_time, threshold_hours=2):
    """Check if food expires within threshold_hours."""
    from datetime import datetime, timedelta
    if not expiry_time:
        return False
    return expiry_time <= datetime.now() + timedelta(hours=threshold_hours)
