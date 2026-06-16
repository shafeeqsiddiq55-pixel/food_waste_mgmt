# ============================================================
# routes/ngo.py - NGO/Receiver Routes
# ============================================================

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import mysql

ngo_bp = Blueprint('ngo', __name__)

# TODO: Implement NGO routes
# - Dashboard
# - View Available Donations
# - Request Pickup
# - View Requests
# - View History
# - Organization Profile

@ngo_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'ngo':
        flash('Unauthorized access', 'error')
        return redirect(url_for('auth.login'))
    # TODO: Implement dashboard logic
    return render_template('ngo/dashboard.html')


@ngo_bp.route('/available-donations')
def available_donations():
    # TODO: Get available donations
    return render_template('ngo/available_donations.html')


@ngo_bp.route('/request-donation/<int:donation_id>', methods=['POST'])
def request_donation(donation_id):
    # TODO: Implement pickup request creation
    pass
