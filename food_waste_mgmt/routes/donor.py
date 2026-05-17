# ============================================================
# routes/donor.py - Donor Blueprint
# ============================================================

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from app import mysql
from utils.helpers import login_required, role_required, send_notification, allowed_file
import os
from werkzeug.utils import secure_filename
from datetime import datetime

donor_bp = Blueprint('donor', __name__)

# ============================================================
# DONOR DASHBOARD
# ============================================================
@donor_bp.route('/dashboard')
@login_required
@role_required('donor')
def dashboard():
    cur = mysql.connection.cursor()
    donor_id = session['user_id']

    # Stats
    cur.execute("SELECT COUNT(*) as cnt FROM food_donations WHERE donor_id=%s", (donor_id,))
    total_donations = cur.fetchone()['cnt']

    cur.execute("SELECT COALESCE(SUM(quantity),0) as total FROM food_donations WHERE donor_id=%s AND status='completed'", (donor_id,))
    meals_saved = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) as cnt FROM food_donations WHERE donor_id=%s AND status='available'", (donor_id,))
    active_donations = cur.fetchone()['cnt']

    # Recent donations
    cur.execute("""
        SELECT fd.*, u.name as donor_name,
               pr.status as pickup_status, u2.name as ngo_name
        FROM food_donations fd
        LEFT JOIN users u ON fd.donor_id = u.id
        LEFT JOIN pickup_requests pr ON pr.donation_id = fd.id AND pr.status NOT IN ('cancelled')
        LEFT JOIN users u2 ON pr.ngo_id = u2.id
        WHERE fd.donor_id = %s
        ORDER BY fd.created_at DESC LIMIT 10
    """, (donor_id,))
    donations = cur.fetchall()

    # Unread notifications
    cur.execute("""
        SELECT * FROM notifications WHERE user_id=%s AND is_read=FALSE
        ORDER BY created_at DESC LIMIT 5
    """, (donor_id,))
    notifications = cur.fetchall()

    cur.close()

    return render_template('donor/dashboard.html',
                           total_donations=total_donations,
                           meals_saved=meals_saved,
                           active_donations=active_donations,
                           donations=donations,
                           notifications=notifications)


# ============================================================
# POST NEW DONATION
# ============================================================
@donor_bp.route('/donate', methods=['GET', 'POST'])
@login_required
@role_required('donor')
def donate():
    if request.method == 'POST':
        food_name = request.form.get('food_name', '').strip()
        food_type = request.form.get('food_type', 'veg')
        quantity = request.form.get('quantity', 0)
        description = request.form.get('description', '').strip()
        expiry_time = request.form.get('expiry_time')
        pickup_start = request.form.get('pickup_start_time')
        pickup_end = request.form.get('pickup_end_time')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        address = request.form.get('address', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        contact_phone = request.form.get('contact_phone', '').strip()
        special_notes = request.form.get('special_notes', '').strip()

        if not all([food_name, quantity, expiry_time, pickup_start, pickup_end, latitude, longitude, address]):
            flash('Please fill all required fields.', 'danger')
            return render_template('donor/donate.html',
                                   maps_key=current_app.config['GOOGLE_MAPS_API_KEY'])

        # Handle food image upload
        image_url = None
        if 'food_image' in request.files:
            file = request.files['food_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"food_{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                image_url = f"/static/uploads/{filename}"

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO food_donations
            (donor_id, food_name, food_type, quantity, description, expiry_time,
             pickup_start_time, pickup_end_time, latitude, longitude, address,
             contact_person, contact_phone, special_notes, image_url)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (session['user_id'], food_name, food_type, quantity, description,
              expiry_time, pickup_start, pickup_end, latitude, longitude,
              address, contact_person, contact_phone, special_notes, image_url))
        mysql.connection.commit()

        donation_id = cur.lastrowid

        # Notify all active NGOs about new donation
        cur.execute("SELECT id FROM users WHERE role='ngo' AND is_active=TRUE")
        ngos = cur.fetchall()
        for ngo in ngos:
            send_notification(cur, ngo['id'],
                              'New Food Available!',
                              f'New donation posted: {food_name} ({quantity} people) at {address}',
                              'info', donation_id)

        mysql.connection.commit()
        cur.close()

        flash('Donation posted successfully! NGOs will be notified.', 'success')
        return redirect(url_for('donor.my_donations'))

    return render_template('donor/donate.html',
                           maps_key=current_app.config['GOOGLE_MAPS_API_KEY'])


# ============================================================
# MY DONATIONS LIST
# ============================================================
@donor_bp.route('/my-donations')
@login_required
@role_required('donor')
def my_donations():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT fd.*,
               pr.status as pickup_status,
               pr.id as request_id,
               u.name as ngo_name,
               u.phone as ngo_phone,
               u.organization_name as ngo_org
        FROM food_donations fd
        LEFT JOIN pickup_requests pr ON pr.donation_id = fd.id AND pr.status NOT IN ('cancelled')
        LEFT JOIN users u ON pr.ngo_id = u.id
        WHERE fd.donor_id = %s
        ORDER BY fd.created_at DESC
    """, (session['user_id'],))
    donations = cur.fetchall()
    cur.close()
    return render_template('donor/my_donations.html', donations=donations)


# ============================================================
# DELETE / REMOVE DONATION
# ============================================================
@donor_bp.route('/delete-donation/<int:donation_id>', methods=['POST'])
@login_required
@role_required('donor')
def delete_donation(donation_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE food_donations SET status='removed'
        WHERE id=%s AND donor_id=%s
    """, (donation_id, session['user_id']))
    mysql.connection.commit()
    cur.close()
    flash('Donation removed.', 'info')
    return redirect(url_for('donor.my_donations'))


# ============================================================
# DONATION HISTORY / ANALYTICS
# ============================================================
@donor_bp.route('/history')
@login_required
@role_required('donor')
def history():
    cur = mysql.connection.cursor()
    donor_id = session['user_id']

    cur.execute("""
        SELECT fd.*, pr.collected_time, pr.beneficiaries_count,
               u.name as ngo_name, u.organization_name as ngo_org
        FROM food_donations fd
        LEFT JOIN pickup_requests pr ON pr.donation_id = fd.id
        LEFT JOIN users u ON pr.ngo_id = u.id
        WHERE fd.donor_id=%s AND fd.status IN ('completed','collected')
        ORDER BY fd.created_at DESC
    """, (donor_id,))
    history = cur.fetchall()

    # Monthly stats for chart
    cur.execute("""
        SELECT DATE_FORMAT(created_at, '%%Y-%%m') as month,
               COUNT(*) as donations,
               COALESCE(SUM(quantity),0) as meals
        FROM food_donations
        WHERE donor_id=%s
        GROUP BY month ORDER BY month DESC LIMIT 12
    """, (donor_id,))
    monthly_stats = cur.fetchall()

    cur.close()
    return render_template('donor/history.html', history=history, monthly_stats=monthly_stats)
