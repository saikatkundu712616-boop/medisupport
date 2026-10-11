MediStore — Online Pharmacy Management System
A complete Django-based pharmacy management system with medicine ordering, AI doctor consultation, lab test booking, cart, checkout, and order tracking.



📋 Table of Contents
Features

Tech Stack

Screenshots

Installation

Configuration

Usage

Project Structure

API Endpoints

Contributing

License

Contact

✨ Features
🛒 Shopping & Orders
Browse medicines by category

Advanced search with filters

Shopping cart with quantity management

Wishlist for favorite medicines

Buy Now (skip cart) option

Order tracking with timeline

Order cancellation with reason

💊 Medicine Management
Detailed medicine pages with composition

Stock status indicators (In Stock / Low / Out)

Discount badges and MRP comparison

Prescription-required flag

Related medicines suggestions

🤖 AI Doctor
Symptom-based consultation

Instant health recommendations

Medicine suggestions

24/7 availability

🧪 Lab Tests
Home sample collection booking

Individual tests and health packages

3-step booking modal (Details → Payment → Confirm)

Multiple payment options (Online / Cash / Pay at Lab)

PDF report delivery

👤 User Management
User registration and login

Profile management

Multiple saved addresses

Password change

Order history

📄 Prescription Upload
Upload prescription images for verification

Secure file handling

🔐 Admin Panel
Django admin integration

Manage medicines, categories, suppliers

Order management dashboard

Inventory tracking

Low stock alerts

Sales reports

🛠 Tech Stack
Layer	Technology
Backend	Django 4.x, Python 3.12
Database	SQLite (dev), PostgreSQL (prod ready)
Frontend	Bootstrap 5, Font Awesome 6
Authentication	Django built-in auth
File Storage	Django media files
Version Control	Git & GitHub

🚀 Installation
Prerequisites
Python 3.10+ — Download

Git — Download

Pip — usually bundled with Python

Step 1: Clone the Repository
bash
git clone https://github.com/YOUR-USERNAME/medisupport.git
cd medisupport
Step 2: Create a Virtual Environment
Windows (PowerShell):

powershell
python -m venv venv
venv\Scripts\activate
macOS / Linux:

bash
python3 -m venv venv
source venv/bin/activate
Step 3: Install Dependencies
bash
pip install -r requirements.txt
If no requirements.txt, install manually:

bash
pip install django
pip install pillow
pip install django-crispy-forms
Step 4: Apply Migrations
bash
python manage.py makemigrations
python manage.py migrate
Step 5: Create Superuser
bash
python manage.py createsuperuser
Enter:

Username: admin

Email: admin@example.com

Password: (your choice)

Step 6: Run Development Server
bash
python manage.py runserver
Open: http://127.0.0.1:8000/

⚙️ Configuration
Environment Variables (Optional)
Create a .env file in the project root:
