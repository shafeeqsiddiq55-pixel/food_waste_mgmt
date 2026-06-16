# ============================================================
# routes/donor.py - Donor Routes
# ============================================================

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import mysql

donor_bp = Blueprint('donor', __name__)

# TODO: Implement donor routes
# - Dashboard
# - Create Donation
# - View Donations
# - Edit Donation
# - Delete Donation
# - View Pickup Requests

@donor_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'donor':
        flash('Unauthorized access', 'error')
        return redirect(url_for('auth.login'))
    # TODO: Implement dashboard logic
    return render_template('donor/dashboard.html')


@donor_bp.route('/donation/new', methods=['GET', 'POST'])
def create_donation():
    if request.method == 'POST':
        # TODO: Implement donation creation
        pass
    return render_template('donor/create_donation.html')


@donor_bp.route('/donations')
def view_donations():
    # TODO: Get donor's donations
    return render_template('donor/view_donations.html')
