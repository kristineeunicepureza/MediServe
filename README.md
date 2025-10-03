##MediServe Repository 

MediServe: Community Health Portal
Project Overview
The purpose of the MediServe project is to address current inefficiencies and challenges faced by barangay residents and local health center staff in accessing and managing medical services. This platform transforms manual processes into a convenient, centralized digital system.

Currently: Residents, particularly the elderly and those with disabilities, must physically visit the health center to check medicine availability, which is time-consuming and inconvenient. Manual medicine tracking also leads to delays, errors, and inaccurate records.

MediServe Solution: This platform provides a centralized portal to improve healthcare delivery by offering residents a convenient way to check medicine inventory and access health-related news, while empowering medical staff with efficient tools for inventory management, order fulfillment, and data recording.

Key Features
The MediServe application is split into two primary interfaces: the User Portal (Blue Theme) and the Admin/Staff Dashboard (Red/Yellow Theme).

1. User Portal (Barangay Residents)
Feature

Description

Medicine Catalog

Browse available medicines in a clean, card-based UI with real-time stock status (In Stock, Low Stock, Out of Stock).

Online Ordering

Add items to a Current Order cart, submit the final order, and confirm total price.

Queue Management

View the Queue Status after submission, showing the assigned queue number and estimated wait time for pickup.

Profile & History

View/Edit personal details, update settings (Font Size, Notifications), and review Order History.

Announcements

Access latest health-related news, vaccine drives, and center updates in a unified feed.

2. Admin Portal (Health Center Staff)
Feature

Description

Admin Dashboard

Centralized hub accessible only by staff (via /management/menu/).

Stock Management

View and edit medicine quantities and unit prices in real-time, with color-coded alerts for low stock.

Order Fulfillment

View orders categorized as 'Processing' or 'Shipped' and use dedicated buttons to Mark Shipped or Mark Completed.

Analytics & Records

View basic sales KPIs (Key Performance Indicators) and access a detailed Transaction Log of all inventory changes.

Technical Stack
This project is built using the Django Web Framework (Python).

Backend: Python 3.x, Django 5.x.

Database: SQLite (default for development).

Frontend: Django Templates, HTML/CSS (Inline/Custom Stylesheets), Font Awesome Icons, JavaScript (for toggles and form logic).

Setup and Installation (Development)
Follow these steps to get MediServe running locally:

1. Environment Setup
# 1. Create a virtual environment
python -m venv venv

# 2. Activate the environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install Django (assuming requirements are minimal)
pip install django

2. Database and Superuser Setup
You must create the database and an administrator account to access the staff features.

# 4. Apply migrations (creates initial database tables)
python manage.py migrate

# 5. Create a Superuser (Admin Account)
python manage.py createsuperuser

# NOTE: When entering the password, characters will not appear on the screen.

3. Running the Server
# 6. Start the Django development server
python manage.py runserver

4. Accessing the Application
Role

Link

Credentials

User Access

https://www.google.com/search?q=http://127.0.0.1:8000/

Use the Sign Up form to create a new user.

Admin Access

https://www.google.com/search?q=http://127.0.0.1:8000/management/menu/

Use the Superuser credentials created in Step 5.


