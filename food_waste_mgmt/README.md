# 🌾 FoodBridge – Food Waste Management System

A production-level full-stack web application that reduces food waste by connecting
food donors (hotels, marriage halls, events) with NGOs to feed the needy.

---

## 📁 Project Structure

```
food_waste_mgmt/
├── app.py                    ← Flask app factory & entry point
├── config.py                 ← Configuration (DB, keys, mail)
├── requirements.txt          ← Python dependencies
├── schema.sql                ← MySQL database schema
├── .env                      ← Environment variables (create this)
│
├── routes/
│   ├── auth.py               ← Login, register, profile
│   ├── donor.py              ← Donor dashboard & donations
│   ├── ngo.py                ← NGO dashboard & pickups
│   ├── admin.py              ← Admin panel
│   └── api.py                ← REST API (AJAX/Maps)
│
├── utils/
│   └── helpers.py            ← Decorators, notifications, helpers
│
├── static/
│   ├── css/style.css         ← Main stylesheet
│   ├── js/main.js            ← Frontend JavaScript
│   └── uploads/              ← Food images (auto-created)
│
└── templates/
    ├── base.html             ← Base layout with navbar
    ├── index.html            ← Landing page
    ├── auth/
    │   ├── login.html
    │   ├── register.html
    │   └── profile.html
    ├── donor/
    │   ├── dashboard.html
    │   ├── donate.html
    │   ├── my_donations.html
    │   └── history.html
    ├── ngo/
    │   ├── dashboard.html
    │   ├── available_donations.html
    │   └── my_pickups.html
    ├── admin/
    │   ├── dashboard.html
    │   ├── users.html
    │   ├── donations.html
    │   └── statistics.html
    └── errors/
        ├── 404.html
        ├── 403.html
        └── 500.html
```

---

## ⚙️ Setup Instructions

### 1. Prerequisites

- Python 3.9+
- MySQL 8.0+
- A Google Maps API Key (free tier works)

### 2. Clone / Extract the Project

```bash
cd food_waste_mgmt
```

### 3. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note for Windows:** If `mysqlclient` fails, install it via:
> `pip install mysqlclient` or download the wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/

### 5. Set Up MySQL Database

```bash
# Login to MySQL
mysql -u root -p

# Run the schema
source /path/to/food_waste_mgmt/schema.sql
# OR
mysql -u root -p < schema.sql
```

### 6. Create the `.env` File

Create a file named `.env` in the project root:

```env
SECRET_KEY=your-super-secret-key-change-this
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=food_waste_mgmt
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# Optional - Email notifications
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER=noreply@foodwaste.com
```

### 7. Create Default Admin Password

After running the schema, update the admin password:

```python
# Run this once in Python console:
from flask_bcrypt import generate_password_hash
print(generate_password_hash('Admin@123').decode('utf-8'))
```

Then update the admin user in MySQL:
```sql
USE food_waste_mgmt;
UPDATE users SET password_hash='<paste_hash_here>' WHERE email='admin@foodwaste.com';
```

### 8. Run the Application

```bash
python app.py
```

Visit: **http://localhost:5000**

---

## 🔐 Default Credentials

| Role  | Email                  | Password   |
|-------|------------------------|------------|
| Admin | admin@foodwaste.com    | Admin@123  |

Register new donor/NGO accounts from the homepage.

---

## 🗺️ Google Maps API Setup

1. Go to https://console.cloud.google.com
2. Create a new project → Enable:
   - **Maps JavaScript API**
   - **Geocoding API**
   - **Directions API**
3. Create credentials → API Key
4. Paste the key in your `.env` file

---

## 🎯 User Roles & Features

### 🏨 Food Donor
- Register as a Donor (hotel, marriage hall, event organizer)
- Post food donations with: name, type, quantity, expiry, pickup time, location
- Upload food photos
- View real-time status (Available → Accepted → Collected → Completed)
- Get notified when NGO accepts
- View donation history & analytics

### 🤝 NGO / Food Collector
- Register as an NGO
- Browse available donations on a live map
- Filter by food type and distance
- Accept pickup requests (notifies donor instantly)
- Get Google Maps directions to pickup location
- Mark as Collected (with beneficiary count)
- Track all pickups with status history

### ⚙️ Admin
- Manage all users (activate/deactivate)
- View and remove all donations
- Platform-wide analytics (charts, top donors, top NGOs)
- Monitor expired/fake listings

---

## 📊 Database Tables

| Table            | Purpose                               |
|------------------|---------------------------------------|
| users            | All user accounts (donor/ngo/admin)   |
| food_donations   | Posted food donations                 |
| pickup_requests  | NGO pickup requests                   |
| notifications    | In-app notification system            |
| donation_stats   | Daily aggregated stats                |

---

## 🔄 Donation Status Flow

```
AVAILABLE → ACCEPTED → COLLECTED → COMPLETED
                                 ↘ EXPIRED (auto)
                                 ↘ REMOVED (admin/donor)
```

---

## 🚀 Key Features Implemented

- [x] Role-based authentication (Donor / NGO / Admin)
- [x] Password hashing with bcrypt
- [x] Food donation posting with map pin
- [x] Google Maps live donation markers
- [x] NGO nearby donation list with distance
- [x] Accept → Collect → Complete workflow
- [x] Real-time in-app notification system
- [x] Auto-expire donations (background scheduler)
- [x] Food safety warnings (< 2 hour expiry alert)
- [x] Admin panel with charts (Chart.js)
- [x] Food image uploads
- [x] Responsive Bootstrap 5 UI
- [x] REST API for AJAX/map data
- [x] Donation history tracking
- [x] Platform analytics (meals saved, top donors/NGOs)

---

## 🛠️ Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Backend     | Python 3.9 + Flask 3.0              |
| Database    | MySQL 8.0 via Flask-MySQLdb         |
| Frontend    | Bootstrap 5.3 + Vanilla JS          |
| Maps        | Google Maps JavaScript API          |
| Auth        | Flask-Bcrypt (password hashing)     |
| Email       | Flask-Mail (optional)               |
| Scheduler   | APScheduler (auto-expire)           |
| Charts      | Chart.js                            |
| Fonts       | Google Fonts (Plus Jakarta Sans, Fraunces) |

---

## 📝 Notes for Submission

- All passwords are bcrypt-hashed — never stored in plain text
- CSRF protection can be added via `Flask-WTF`
- For production: use `gunicorn` + `nginx` + set `DEBUG=False`
- Google Maps API key should be restricted by domain in production
- Email notifications require valid SMTP credentials in `.env`

---

*Built for final year Computer Science project — FoodBridge, 2025*
