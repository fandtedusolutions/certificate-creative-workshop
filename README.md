# Natdemy Creative Workshop - Student Online Certificate & Leads Portal

A Django web application built for **Natdemy** to distribute online certificates of participation to students and simultaneously capture qualified student leads.

---

## 🌟 Workflow Overview

1. **Admin Shares Link**: The admin shares the workshop certificate link (`http://<server-ip>:8000/`) with students via WhatsApp, email, QR code, or presentation slide.
2. **Student Fills Form**:
   - **Name**: Student's full name (only this name changes on the certificate).
   - **Class**: Dropdown selection (`1st Year`, `2nd Year`, `3rd Year`).
   - **Phone Number**: WhatsApp / Mobile number.
3. **Get Certificate**:
   - Clicking **"Get Certificate"** automatically records the student lead in the database.
   - The candidate name is rendered into the certificate template using calligraphic typography in matching dark navy `#14334c` with an elegant accent underline.
4. **Certificate Download & Leads Capture**:
   - Students can download both **Print-Ready High-Res PDF (A4 300 DPI)** and **High-Res JPG (3508 &times; 2480 px)**.
   - Students can share directly to WhatsApp or copy their unique certificate link.
   - Admins can log in to `/admin/` to view real-time leads, track downloads, and export all leads to **Excel (.xlsx)** or **CSV**.

---

## 🚀 Quick Start Guide

### 1. Run the Development Server
```bash
./venv/bin/python manage.py runserver 0.0.0.0:8000
```

### 2. Student Portal URL (Share with students)
```
http://localhost:8000/
```
*(Or your local IP / domain, e.g., `http://192.168.1.X:8000/` or ngrok tunnel)*

### 3. Admin Leads Portal
```
http://localhost:8000/admin/
```
- **Username**: `admin`
- **Password**: `admin123`

---

## 📊 Admin Features & Lead Export

Inside the Admin panel (`/admin/certificates/studentlead/`):
- **Real-Time Lead List**: See Student Name, Class Badge, Phone Number, Download Count, and Timestamp.
- **Search & Filters**: Quickly filter by Class (1st, 2nd, 3rd Year) or registration date; search by name or phone.
- **Export to Excel (.xlsx)**: Select leads and choose **"📥 Export Selected Leads to Excel (.xlsx)"** from the Action dropdown.
- **Export to CSV**: Select leads and choose **"📄 Export Selected Leads to CSV"**.
- **Instant Certificate Preview**: Click "View" or "Student Page" directly from any row in the admin list.

---

## 🎨 Certificate Specifications

- **Dimensions**: 3508 &times; 2480 pixels (A4 standard at 300 DPI)
- **Dynamic Elements**: Candidate Name only (auto-scaled dynamically so long names never clip or overflow margins).
- **Static Template Elements Preserved**:
  - Certificate of Participation
  - "THIS IS TO CERTIFY THAT"
  - Workshop details: *Creative Workshop conducted by Natdemy on 23 November 2026 at St. Joseph's College Devagiri, Kozhikode*
  - Signature: *Muhammed Thashmeer Kp, Chief Academic Officer (CAO)*
  - Natdemy Logo & Best Excellence 2026 Gold Seal

---

## 🛠️ Project Structure

```text
Cerificate-creative-workshop/
├── certificate_project/     # Django settings, root URLs, WSGI/ASGI
├── certificates/           # Main certificate app
│   ├── models.py           # StudentLead model
│   ├── forms.py            # StudentLeadForm with class dropdown & phone validation
│   ├── views.py            # Form view, detail view, preview & download views
│   ├── admin.py            # Customized admin with Excel & CSV export actions
│   ├── utils.py            # Pillow 300 DPI certificate generator
│   ├── urls.py             # App routing
│   └── tests.py            # Automated tests
├── static/                 # Clean certificate template & fonts
│   └── certificates/
│       ├── images/template.jpg
│       └── fonts/AlexBrush-Regular.ttf
├── templates/              # Responsive Bootstrap 5 templates
│   ├── base.html
│   └── certificates/
│       ├── index.html      # Student registration form
│       └── detail.html     # Certificate preview & download hub
└── manage.py
```

---

## 🧪 Running Tests

To verify all test cases:
```bash
./venv/bin/python manage.py test
```

