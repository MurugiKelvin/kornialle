# Kornialle — Django Property Booking Platform

A full-stack Django web application for property discovery and booking, inspired by the Kornialle.net design.

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install django pillow
```

### 2. Apply migrations

```bash
cd kornialle
python manage.py makemigrations stays
python manage.py migrate
```

### 3. Seed demo data

```bash
python manage.py seed_demo_data
```

This creates:
- ✅ Superuser: `admin` / `admin1234`
- 🏨 5 featured properties (hotel, cabin, villa, apartment)
- 💰 Price rules per property
- ⭐ Verified reviews

### 4. Start the server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

---

## 🔑 Features

### Public Features
- **Homepage** — Hero search, featured properties, city destinations, reviews
- **Property Listing** — Filter by type, city, keyword search
- **Property Detail** — Full info, pricing tiers, amenity badges, booking form, reviews
- **Booking** — Guest details form, check-in/check-out, confirmation page

### User Features
- **Register** — Full name, email, phone, city, newsletter opt-in, welcome code
- **Sign In / Sign Out** — Session-based authentication
- **Dashboard** — View all bookings with status, edit profile info

### Admin Panel (`/admin/`)
- **Properties** — Add, edit, delete; set featured; upload images or use URL; manage amenities
- **Price Rules** — Per-property seasonal pricing with discount %; inline on property page
- **Bookings** — View all bookings, update status (Pending → Confirmed → Completed)
- **Reviews** — Verify or remove reviews
- **Users & Profiles** — Manage accounts

---

## 📁 Project Structure

```
kornialle/
├── manage.py
├── kornialle/               # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── stays/                   # Main app
│   ├── models.py            # Property, PriceRule, Booking, Review, UserProfile
│   ├── views.py             # All views
│   ├── forms.py             # Register, Booking, Review, Profile forms
│   ├── admin.py             # Customized Django admin
│   ├── urls.py
│   ├── signals.py           # Auto-create UserProfile on signup
│   └── management/commands/
│       └── seed_demo_data.py
├── templates/
│   ├── base.html            # Nav, footer, messages
│   ├── registration/
│   │   ├── login.html
│   │   └── register.html
│   └── stays/
│       ├── home.html
│       ├── property_list.html
│       ├── property_detail.html
│       ├── dashboard.html
│       └── booking_confirmation.html
└── static/
```

---

## 🛠 Admin Guide

### Adding a Property
1. Go to `/admin/` → **Properties** → **Add Property**
2. Fill in: Name, Type, City, State, Address, Description
3. Upload image or paste external image URL
4. Add amenities as comma-separated: `Free WiFi, Pool, Breakfast`
5. Check **Is Featured** to show on homepage
6. Add **Price Rules** inline (standard, weekend, peak, off-peak pricing with optional discount %)

### Managing Bookings
- Go to **Bookings** in admin
- Update the **Status** column directly from the list view
- Filter by property, status, or date

### Verifying Reviews
- Go to **Reviews** in admin
- Toggle **Is Verified** — only verified reviews show as "✓ Verified stay"

---

## 🔒 Security Notes for Production

1. Set `DEBUG = False` in settings.py
2. Set `SECRET_KEY` from environment variable
3. Configure `ALLOWED_HOSTS` with your domain
4. Set up proper email backend (SMTP)
5. Use PostgreSQL instead of SQLite
6. Set up static file serving (WhiteNoise or CDN)

```python
# settings.py production additions
import os
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```
