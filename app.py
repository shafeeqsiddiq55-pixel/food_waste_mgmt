# ============================================================
# app.py - Main Flask Application
# ============================================================

from flask import Flask, render_template, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler
import os
from config import config

# --- Initialize Extensions ---
mysql = MySQL()
bcrypt = Bcrypt()
mail = Mail()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # --- Bind Extensions ---
    mysql.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    # --- Ensure upload folder exists ---
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # --- Register Blueprints ---
    from routes.auth import auth_bp
    from routes.donor import donor_bp
    from routes.ngo import ngo_bp
    from routes.admin import admin_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(donor_bp, url_prefix='/donor')
    app.register_blueprint(ngo_bp, url_prefix='/ngo')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    # --- Auto-expire old donations ---
    def auto_expire_donations():
        with app.app_context():
            try:
                cur = mysql.connection.cursor()
                cur.execute("""
                    UPDATE food_donations 
                    SET status = 'expired' 
                    WHERE expiry_time < NOW() 
                    AND status IN ('available', 'accepted')
                """)
                mysql.connection.commit()
                cur.close()
            except Exception as e:
                print(f"Auto-expire error: {e}")

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=auto_expire_donations,
        trigger='interval',
        seconds=app.config['AUTO_EXPIRE_CHECK_INTERVAL']
    )
    scheduler.start()

    # --- Home Route ---
    @app.route('/')
    def index():
        if 'user_id' in session:
            role = session.get('role')
            if role == 'donor':
                return redirect(url_for('donor.dashboard'))
            elif role == 'ngo':
                return redirect(url_for('ngo.dashboard'))
            elif role == 'admin':
                return redirect(url_for('admin.dashboard'))
        return render_template('index.html')

    # --- Error Handlers ---
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    return app


if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)
