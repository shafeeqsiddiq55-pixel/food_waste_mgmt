# ============================================================
# routes/api.py - REST API Blueprint (for AJAX/Maps)
# ============================================================

from flask import Blueprint, jsonify, request, session
from app import mysql
from utils.helpers import login_required

api_bp = Blueprint('api', __name__)

# ============================================================
# GET ALL AVAILABLE DONATIONS (for map markers)
# ============================================================
@api_bp.route('/donations/map')
def donations_map():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT fd.id, fd.food_name, fd.food_type, fd.quantity,
               fd.address, fd.latitude, fd.longitude, fd.expiry_time,
               fd.pickup_start_time, fd.pickup_end_time, fd.status,
               fd.contact_phone, fd.special_notes, fd.image_url,
               u.name as donor_name, u.organization_name as donor_org
        FROM food_donations fd
        JOIN users u ON fd.donor_id=u.id
        WHERE fd.status='available' AND fd.expiry_time > NOW()
        AND fd.latitude IS NOT NULL AND fd.longitude IS NOT NULL
    """)
    donations = cur.fetchall()
    cur.close()

    # Convert datetime to string for JSON
    result = []
    for d in donations:
        d['expiry_time'] = str(d['expiry_time']) if d['expiry_time'] else None
        d['pickup_start_time'] = str(d['pickup_start_time']) if d['pickup_start_time'] else None
        d['pickup_end_time'] = str(d['pickup_end_time']) if d['pickup_end_time'] else None
        result.append(d)

    return jsonify({'success': True, 'donations': result})


# ============================================================
# MARK NOTIFICATION AS READ
# ============================================================
@api_bp.route('/notifications/read/<int:notif_id>', methods=['POST'])
@login_required
def mark_notification_read(notif_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE notifications SET is_read=TRUE
        WHERE id=%s AND user_id=%s
    """, (notif_id, session['user_id']))
    mysql.connection.commit()
    cur.close()
    return jsonify({'success': True})


# ============================================================
# GET UNREAD NOTIFICATION COUNT
# ============================================================
@api_bp.route('/notifications/count')
@login_required
def notification_count():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT COUNT(*) as cnt FROM notifications
        WHERE user_id=%s AND is_read=FALSE
    """, (session['user_id'],))
    count = cur.fetchone()['cnt']
    cur.close()
    return jsonify({'count': count})


# ============================================================
# GET ALL NOTIFICATIONS
# ============================================================
@api_bp.route('/notifications/all')
@login_required
def all_notifications():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT * FROM notifications WHERE user_id=%s
        ORDER BY created_at DESC LIMIT 20
    """, (session['user_id'],))
    notifications = cur.fetchall()
    for n in notifications:
        n['created_at'] = str(n['created_at'])
    cur.close()
    return jsonify({'notifications': notifications})


# ============================================================
# DONATION DETAIL
# ============================================================
@api_bp.route('/donation/<int:donation_id>')
def donation_detail(donation_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT fd.*, u.name as donor_name, u.organization_name, u.phone as donor_phone
        FROM food_donations fd JOIN users u ON fd.donor_id=u.id
        WHERE fd.id=%s
    """, (donation_id,))
    d = cur.fetchone()
    cur.close()
    if not d:
        return jsonify({'success': False, 'message': 'Not found'}), 404
    d['expiry_time'] = str(d['expiry_time'])
    d['pickup_start_time'] = str(d['pickup_start_time'])
    d['pickup_end_time'] = str(d['pickup_end_time'])
    d['created_at'] = str(d['created_at'])
    return jsonify({'success': True, 'donation': d})
