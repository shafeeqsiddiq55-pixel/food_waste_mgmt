# ============================================================
# routes/ngo.py - NGO Blueprint
# ============================================================

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
from app import mysql
from utils.helpers import login_required, role_required, send_notification
from datetime import datetime
import math

ngo_bp = Blueprint('ngo', __name__)

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two lat/lng points in km."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# ============================================================
# NGO DASHBOARD
# ============================================================
@ngo_bp.route('/dashboard')
@login_required
@role_required('ngo')
def dashboard():
    cur = mysql.connection.cursor()
    ngo_id = session['user_id']

    # Stats
    cur.execute("SELECT COUNT(*) as cnt FROM pickup_requests WHERE ngo_id=%s", (ngo_id,))
    total_pickups = cur.fetchone()['cnt']

    cur.execute("SELECT COALESCE(SUM(fd.quantity),0) as meals FROM pickup_requests pr JOIN food_donations fd ON pr.donation_id=fd.id WHERE pr.ngo_id=%s AND pr.status='completed'", (ngo_id,))
    meals_collected = cur.fetchone()['meals']

    cur.execute("SELECT COUNT(*) as cnt FROM pickup_requests WHERE ngo_id=%s AND status IN ('accepted','in_transit')", (ngo_id,))
    active_pickups = cur.fetchone()['cnt']

    # Available donations nearby
    cur.execute("""
        SELECT fd.*, u.name as donor_name, u.organization_name as donor_org, u.phone as donor_phone
        FROM food_donations fd
        JOIN users u ON fd.donor_id = u.id
        WHERE fd.status='available' AND fd.expiry_time > NOW()
        ORDER BY fd.created_at DESC LIMIT 20
    """)
    available_donations = cur.fetchall()

    # My active requests
    cur.execute("""
        SELECT pr.*, fd.food_name, fd.address, fd.latitude, fd.longitude,
               fd.quantity, fd.expiry_time, fd.food_type,
               u.name as donor_name, u.phone as donor_phone, u.organization_name as donor_org
        FROM pickup_requests pr
        JOIN food_donations fd ON pr.donation_id = fd.id
        JOIN users u ON fd.donor_id = u.id
        WHERE pr.ngo_id=%s AND pr.status IN ('accepted','in_transit','pending')
        ORDER BY pr.created_at DESC
    """, (ngo_id,))
    my_requests = cur.fetchall()

    # Notifications
    cur.execute("""
        SELECT * FROM notifications WHERE user_id=%s AND is_read=FALSE
        ORDER BY created_at DESC LIMIT 5
    """, (ngo_id,))
    notifications = cur.fetchall()

    cur.close()

    return render_template('ngo/dashboard.html',
                           available_donations=available_donations,
                           my_requests=my_requests,
                           total_pickups=total_pickups,
                           meals_collected=meals_collected,
                           active_pickups=active_pickups,
                           notifications=notifications,
                           maps_key=current_app.config['GOOGLE_MAPS_API_KEY'])


# ============================================================
# VIEW ALL AVAILABLE DONATIONS (with map)
# ============================================================
@ngo_bp.route('/available-donations')
@login_required
@role_required('ngo')
def available_donations():
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT fd.*, u.name as donor_name, u.organization_name as donor_org, u.phone as donor_phone
        FROM food_donations fd
        JOIN users u ON fd.donor_id = u.id
        WHERE fd.status='available' AND fd.expiry_time > NOW()
        ORDER BY fd.created_at DESC
    """)
    donations = cur.fetchall()

    # Get NGO location for distance calculation
    cur.execute("SELECT latitude, longitude FROM users WHERE id=%s", (session['user_id'],))
    ngo = cur.fetchone()
    cur.close()

    # Add distance if NGO has location
    if ngo and ngo['latitude'] and ngo['longitude']:
        for d in donations:
            if d['latitude'] and d['longitude']:
                d['distance'] = round(haversine_distance(
                    float(ngo['latitude']), float(ngo['longitude']),
                    float(d['latitude']), float(d['longitude'])
                ), 2)
        donations.sort(key=lambda x: x.get('distance', 9999))

    return render_template('ngo/available_donations.html',
                           donations=donations,
                           maps_key=current_app.config['GOOGLE_MAPS_API_KEY'])


# ============================================================
# ACCEPT DONATION (create pickup request)
# ============================================================
@ngo_bp.route('/accept/<int:donation_id>', methods=['POST'])
@login_required
@role_required('ngo')
def accept_donation(donation_id):
    cur = mysql.connection.cursor()
    ngo_id = session['user_id']

    # Check if already accepted
    cur.execute("""
        SELECT id FROM pickup_requests
        WHERE donation_id=%s AND status NOT IN ('cancelled')
    """, (donation_id,))
    if cur.fetchone():
        flash('This donation has already been accepted by another NGO.', 'warning')
        cur.close()
        return redirect(url_for('ngo.available_donations'))

    # Create pickup request
    cur.execute("""
        INSERT INTO pickup_requests (donation_id, ngo_id, status, pickup_time)
        VALUES (%s, %s, 'accepted', NOW())
    """, (donation_id, ngo_id))

    # Update donation status
    cur.execute("UPDATE food_donations SET status='accepted' WHERE id=%s", (donation_id,))

    # Notify donor
    cur.execute("SELECT donor_id, food_name FROM food_donations WHERE id=%s", (donation_id,))
    donation = cur.fetchone()

    cur.execute("SELECT name, organization_name FROM users WHERE id=%s", (ngo_id,))
    ngo = cur.fetchone()

    send_notification(cur, donation['donor_id'],
                      'Pickup Request Accepted!',
                      f'{ngo["organization_name"] or ngo["name"]} has accepted your donation of {donation["food_name"]} and will collect it soon.',
                      'success', donation_id)

    mysql.connection.commit()
    cur.close()

    flash('Pickup request accepted! Please collect the food on time.', 'success')
    return redirect(url_for('ngo.my_pickups'))


# ============================================================
# MARK AS COLLECTED
# ============================================================
@ngo_bp.route('/collected/<int:request_id>', methods=['POST'])
@login_required
@role_required('ngo')
def mark_collected(request_id):
    beneficiaries = request.form.get('beneficiaries', 0)
    cur = mysql.connection.cursor()

    cur.execute("""
        UPDATE pickup_requests SET status='collected', collected_time=NOW(), beneficiaries_count=%s
        WHERE id=%s AND ngo_id=%s
    """, (beneficiaries, request_id, session['user_id']))

    # Get donation info for notification
    cur.execute("""
        SELECT pr.donation_id, fd.donor_id, fd.food_name
        FROM pickup_requests pr JOIN food_donations fd ON pr.donation_id=fd.id
        WHERE pr.id=%s
    """, (request_id,))
    info = cur.fetchone()

    if info:
        cur.execute("UPDATE food_donations SET status='collected' WHERE id=%s", (info['donation_id'],))
        send_notification(cur, info['donor_id'],
                          'Food Successfully Collected!',
                          f'Your donation of {info["food_name"]} has been collected. Thank you for your contribution!',
                          'success', info['donation_id'])

    mysql.connection.commit()
    cur.close()
    flash('Marked as collected! Thank you for making a difference.', 'success')
    return redirect(url_for('ngo.my_pickups'))


# ============================================================
# COMPLETE PICKUP
# ============================================================
@ngo_bp.route('/complete/<int:request_id>', methods=['POST'])
@login_required
@role_required('ngo')
def complete_pickup(request_id):
    cur = mysql.connection.cursor()

    cur.execute("""
        UPDATE pickup_requests SET status='completed', completed_time=NOW()
        WHERE id=%s AND ngo_id=%s
    """, (request_id, session['user_id']))

    cur.execute("""
        SELECT pr.donation_id, fd.donor_id, fd.food_name
        FROM pickup_requests pr JOIN food_donations fd ON pr.donation_id=fd.id
        WHERE pr.id=%s
    """, (request_id,))
    info = cur.fetchone()

    if info:
        cur.execute("UPDATE food_donations SET status='completed' WHERE id=%s", (info['donation_id'],))
        send_notification(cur, info['donor_id'],
                          'Donation Journey Completed!',
                          f'Your donation of {info["food_name"]} has been successfully distributed to the needy. You saved many meals!',
                          'success', info['donation_id'])

    mysql.connection.commit()
    cur.close()
    flash('Pickup completed! Great work.', 'success')
    return redirect(url_for('ngo.my_pickups'))


# ============================================================
# MY PICKUPS
# ============================================================
@ngo_bp.route('/my-pickups')
@login_required
@role_required('ngo')
def my_pickups():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT pr.*, fd.food_name, fd.food_type, fd.address, fd.quantity,
               fd.latitude, fd.longitude, fd.expiry_time, fd.image_url,
               fd.contact_person, fd.contact_phone, fd.special_notes,
               u.name as donor_name, u.organization_name as donor_org, u.phone as donor_phone
        FROM pickup_requests pr
        JOIN food_donations fd ON pr.donation_id = fd.id
        JOIN users u ON fd.donor_id = u.id
        WHERE pr.ngo_id = %s
        ORDER BY pr.created_at DESC
    """, (session['user_id'],))
    pickups = cur.fetchall()
    cur.close()
    return render_template('ngo/my_pickups.html', pickups=pickups,
                           maps_key=current_app.config['GOOGLE_MAPS_API_KEY'])
