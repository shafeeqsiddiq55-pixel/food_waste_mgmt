# ============================================================
# routes/auth.py - Authentication Blueprint
# ============================================================

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from flask_bcrypt import generate_password_hash, check_password_hash
from app import mysql
from utils.helpers import send_notification
import re

auth_bp = Blueprint('auth', __name__)

# --- Helper: Validate Email ---
def is_valid_email(email):
    return re.match(r'^[^@]+@[^@]+\.[^@]+$', email)

# ============================================================
# REGISTER
# ============================================================
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'donor')
        phone = request.form.get('phone', '').strip()
        organization_name = request.form.get('organization_name', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        latitude = request.form.get('latitude') or None
        longitude = request.form.get('longitude') or None

        # Validations
        if not all([name, email, password, role]):
            flash('All required fields must be filled.', 'danger')
            return render_template('auth/register.html')

        if not is_valid_email(email):
            flash('Invalid email address.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        if role not in ['donor', 'ngo']:
            flash('Invalid role selected.', 'danger')
            return render_template('auth/register.html')

        cur = mysql.connection.cursor()

        # Check if email already exists
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            flash('Email already registered. Please login.', 'warning')
            cur.close()
            return redirect(url_for('auth.login'))

        # Hash password
        hashed_pw = generate_password_hash(password).decode('utf-8')

        # Insert user
        cur.execute("""
            INSERT INTO users (name, email, password_hash, role, phone, organization_name, address, city, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, email, hashed_pw, role, phone, organization_name, address, city, latitude, longitude))
        mysql.connection.commit()

        new_id = cur.lastrowid

        # Welcome notification
        send_notification(
            cur,
            user_id=new_id,
            title='Welcome to FoodBridge!',
            message=f'Hello {name}, your account has been created successfully. Start making a difference today!',
            ntype='success'
        )
        mysql.connection.commit()
        cur.close()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


# ============================================================
# LOGIN
# ============================================================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter email and password.', 'danger')
            return render_template('auth/login.html')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND is_active = TRUE", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user['password_hash'], password):
            session.permanent = True
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['email'] = user['email']
            session['role'] = user['role']
            session['organization'] = user['organization_name']

            flash(f'Welcome back, {user["name"]}!', 'success')

            if user['role'] == 'donor':
                return redirect(url_for('donor.dashboard'))
            elif user['role'] == 'ngo':
                return redirect(url_for('ngo.dashboard'))
            elif user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials or account is inactive.', 'danger')

    return render_template('auth/login.html')


# ============================================================
# LOGOUT
# ============================================================
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


# ============================================================
# PROFILE
# ============================================================
@auth_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        organization_name = request.form.get('organization_name', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        latitude = request.form.get('latitude') or None
        longitude = request.form.get('longitude') or None

        cur.execute("""
            UPDATE users SET name=%s, phone=%s, organization_name=%s,
            address=%s, city=%s, latitude=%s, longitude=%s
            WHERE id=%s
        """, (name, phone, organization_name, address, city, latitude, longitude, session['user_id']))
        mysql.connection.commit()
        session['name'] = name
        flash('Profile updated successfully.', 'success')

    cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    cur.close()

    return render_template('auth/profile.html', user=user,
                           maps_key=current_app.config['GOOGLE_MAPS_API_KEY'])
