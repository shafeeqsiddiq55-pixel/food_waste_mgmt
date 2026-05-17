# ============================================================
# routes/admin.py - Admin Blueprint
# ============================================================

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import mysql
from utils.helpers import login_required, role_required

admin_bp = Blueprint('admin', __name__)

# ============================================================
# ADMIN DASHBOARD
# ============================================================
@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    cur = mysql.connection.cursor()

    # Platform stats
    cur.execute("SELECT COUNT(*) as cnt FROM users WHERE role='donor' AND is_active=TRUE")
    total_donors = cur.fetchone()['cnt']

    cur.execute("SELECT COUNT(*) as cnt FROM users WHERE role='ngo' AND is_active=TRUE")
    total_ngos = cur.fetchone()['cnt']

    cur.execute("SELECT COUNT(*) as cnt FROM food_donations")
    total_donations = cur.fetchone()['cnt']

    cur.execute("SELECT COALESCE(SUM(fd.quantity),0) as meals FROM pickup_requests pr JOIN food_donations fd ON pr.donation_id=fd.id WHERE pr.status='completed'")
    total_meals_saved = cur.fetchone()['meals']

    cur.execute("SELECT COUNT(*) as cnt FROM food_donations WHERE status='available' AND expiry_time > NOW()")
    active_donations = cur.fetchone()['cnt']

    cur.execute("SELECT COUNT(*) as cnt FROM food_donations WHERE status='expired'")
    expired_donations = cur.fetchone()['cnt']

    # Recent donations
    cur.execute("""
        SELECT fd.*, u.name as donor_name, u.organization_name as donor_org
        FROM food_donations fd JOIN users u ON fd.donor_id=u.id
        ORDER BY fd.created_at DESC LIMIT 10
    """)
    recent_donations = cur.fetchall()

    # Monthly stats for chart
    cur.execute("""
        SELECT DATE_FORMAT(created_at,'%%Y-%%m') as month, COUNT(*) as cnt,
               COALESCE(SUM(quantity),0) as meals
        FROM food_donations GROUP BY month ORDER BY month DESC LIMIT 12
    """)
    monthly_stats = cur.fetchall()

    cur.close()

    return render_template('admin/dashboard.html',
                           total_donors=total_donors,
                           total_ngos=total_ngos,
                           total_donations=total_donations,
                           total_meals_saved=total_meals_saved,
                           active_donations=active_donations,
                           expired_donations=expired_donations,
                           recent_donations=recent_donations,
                           monthly_stats=monthly_stats)


# ============================================================
# MANAGE USERS
# ============================================================
@admin_bp.route('/users')
@login_required
@role_required('admin')
def manage_users():
    cur = mysql.connection.cursor()
    role_filter = request.args.get('role', '')
    search = request.args.get('search', '')

    query = "SELECT * FROM users WHERE 1=1"
    params = []

    if role_filter:
        query += " AND role=%s"
        params.append(role_filter)
    if search:
        query += " AND (name LIKE %s OR email LIKE %s OR organization_name LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])

    query += " ORDER BY created_at DESC"
    cur.execute(query, params)
    users = cur.fetchall()
    cur.close()

    return render_template('admin/users.html', users=users,
                           role_filter=role_filter, search=search)


# ============================================================
# TOGGLE USER ACTIVE STATUS
# ============================================================
@admin_bp.route('/users/toggle/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
def toggle_user(user_id):
    if user_id == session['user_id']:
        flash('Cannot deactivate your own account.', 'danger')
        return redirect(url_for('admin.manage_users'))

    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET is_active = NOT is_active WHERE id=%s", (user_id,))
    mysql.connection.commit()
    cur.close()
    flash('User status updated.', 'success')
    return redirect(url_for('admin.manage_users'))


# ============================================================
# ALL DONATIONS (admin view)
# ============================================================
@admin_bp.route('/donations')
@login_required
@role_required('admin')
def all_donations():
    cur = mysql.connection.cursor()
    status_filter = request.args.get('status', '')

    query = """
        SELECT fd.*, u.name as donor_name, u.organization_name as donor_org,
               pr.status as pickup_status, u2.name as ngo_name
        FROM food_donations fd
        JOIN users u ON fd.donor_id=u.id
        LEFT JOIN pickup_requests pr ON pr.donation_id=fd.id AND pr.status NOT IN ('cancelled')
        LEFT JOIN users u2 ON pr.ngo_id=u2.id
        WHERE 1=1
    """
    params = []
    if status_filter:
        query += " AND fd.status=%s"
        params.append(status_filter)

    query += " ORDER BY fd.created_at DESC"
    cur.execute(query, params)
    donations = cur.fetchall()
    cur.close()

    return render_template('admin/donations.html', donations=donations, status_filter=status_filter)


# ============================================================
# REMOVE DONATION (admin)
# ============================================================
@admin_bp.route('/donations/remove/<int:donation_id>', methods=['POST'])
@login_required
@role_required('admin')
def remove_donation(donation_id):
    reason = request.form.get('reason', 'Removed by admin')
    cur = mysql.connection.cursor()
    cur.execute("UPDATE food_donations SET status='removed' WHERE id=%s", (donation_id,))
    mysql.connection.commit()
    cur.close()
    flash(f'Donation removed. Reason: {reason}', 'success')
    return redirect(url_for('admin.all_donations'))


# ============================================================
# PLATFORM STATISTICS
# ============================================================
@admin_bp.route('/statistics')
@login_required
@role_required('admin')
def statistics():
    cur = mysql.connection.cursor()

    # By food type
    cur.execute("""
        SELECT food_type, COUNT(*) as cnt, COALESCE(SUM(quantity),0) as meals
        FROM food_donations GROUP BY food_type
    """)
    by_food_type = cur.fetchall()

    # By status
    cur.execute("SELECT status, COUNT(*) as cnt FROM food_donations GROUP BY status")
    by_status = cur.fetchall()

    # Top donors
    cur.execute("""
        SELECT u.name, u.organization_name, COUNT(fd.id) as donations, COALESCE(SUM(fd.quantity),0) as meals
        FROM food_donations fd JOIN users u ON fd.donor_id=u.id
        GROUP BY u.id ORDER BY donations DESC LIMIT 10
    """)
    top_donors = cur.fetchall()

    # Top NGOs
    cur.execute("""
        SELECT u.name, u.organization_name, COUNT(pr.id) as pickups,
               COALESCE(SUM(pr.beneficiaries_count),0) as people_fed
        FROM pickup_requests pr JOIN users u ON pr.ngo_id=u.id
        WHERE pr.status='completed'
        GROUP BY u.id ORDER BY pickups DESC LIMIT 10
    """)
    top_ngos = cur.fetchall()

    cur.close()

    return render_template('admin/statistics.html',
                           by_food_type=by_food_type,
                           by_status=by_status,
                           top_donors=top_donors,
                           top_ngos=top_ngos)
