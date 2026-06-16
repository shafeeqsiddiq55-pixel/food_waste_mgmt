# 🍲 Food Waste Management System

A smart food waste management system connecting donors and receivers to reduce food waste and support communities in need.

## 📋 Project Overview

This system facilitates the connection between food donors (restaurants, grocery stores, event organizers) and food receivers (NGOs, community centers, charitable organizations) to redistribute surplus food efficiently and sustainably.

## 🎯 Key Features

### For Donors
- Register and manage donation listings
- Upload food details with images and expiry information
- Track donation status in real-time
- View pickup requests from NGOs
- Auto-expiration of old donations

### For NGOs/Receivers
- Browse available food donations nearby
- Request food pickups with specific details
- Manage distribution operations
- Track collection history and impact

### For Administrators
- Monitor all donations and pickups
- Manage user accounts and roles
- Generate reports on food waste reduction
- System analytics and insights

## 🏗️ Project Structure

```
food_waste_mgmt/
├── app.py                 # Main Flask application
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── routes/
│   ├── __init__.py
│   ├── auth.py           # Authentication routes
│   ├── donor.py          # Donor routes
│   ├── ngo.py            # NGO routes
│   ├── admin.py          # Admin routes
│   └── api.py            # API endpoints
├── templates/
│   ├── index.html        # Home page
│   ├── auth/             # Authentication templates
│   ├── donor/            # Donor templates
│   ├── ngo/              # NGO templates
│   ├── admin/            # Admin templates
│   └── errors/           # Error pages
├── static/               # CSS, JS, images
├── uploads/              # User uploaded files
├── database/             # Database schema and migrations
└── tests/                # Unit and integration tests
```

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Authentication**: Flask-Bcrypt
- **Email**: Flask-Mail
- **Task Scheduling**: APScheduler
- **Frontend**: HTML, CSS, JavaScript

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL 5.7+
- pip (Python package manager)

### Step 1: Clone the Repository
```bash
git clone https://github.com/shafeeqsiddiq55-pixel/food_waste_mgmt.git
cd food_waste_mgmt
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Setup Environment Variables
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your configuration
```

### Step 5: Setup Database
```bash
# Create database
mysql -u root -p
CREATE DATABASE food_waste_mgmt;
```

### Step 6: Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 📝 Configuration

Update your `.env` file with:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key

MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DB=food_waste_mgmt

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## 🔐 User Roles

1. **Donor** - Individuals or organizations donating food
2. **NGO** - Non-profit organizations receiving food
3. **Admin** - System administrators managing the platform

## 📚 API Documentation

### Available Endpoints

#### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/logout` - User logout

#### Donor Routes
- `GET /donor/dashboard` - Donor dashboard
- `GET /donor/donations` - View all donations
- `POST /donor/donation/new` - Create new donation

#### NGO Routes
- `GET /ngo/dashboard` - NGO dashboard
- `GET /ngo/available-donations` - View available donations
- `POST /ngo/request-donation/<id>` - Request pickup

#### API
- `GET /api/donations` - Get all donations (with filters)
- `GET /api/donation/<id>` - Get donation details

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment instructions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact & Support

For support, email: shafeeqsiddiq55@gmail.com

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Thanks to all contributors
- Special thanks to the open-source community

---

**Last Updated**: June 2024
