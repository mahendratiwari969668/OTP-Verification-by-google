# OTP Verification Authentication System

A secure Flask-based authentication system with:

* User Registration
* User Login
* Password Hashing
* Forgot Password
* OTP Verification via Email
* Password Reset
* Session Management
* SQLite Database

---

## Features

### Authentication

* Register new users
* Login with email and password
* Secure password hashing using Werkzeug
* Session-based authentication

### Password Recovery

* Forgot password functionality
* OTP generation
* OTP verification
* Password reset

### Security

* Passwords are never stored in plain text
* Password hashing with Werkzeug
* Session protection
* Input validation

### Database

* SQLite database
* Automatic table creation
* Email uniqueness enforcement

---

## Project Structure

```text
otp-verification/
│
├── app.py
├── users.db
├── .env
├── requirements.txt
│
├── static/
│   └── style.css
│
├── templates/
│   ├── register.html
│   ├── login.html
│   ├── forgot_password.html
│   ├── verify_otp.html
│   ├── reset_password.html
│   └── dashboard.html
│
└── README.md
```

---

## Technologies Used

* Python
* Flask
* SQLite3
* HTML
* CSS
* Werkzeug
* python-dotenv

---

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd otp-verification
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

Windows

```bash
venv\Scripts\activate
```

Linux/Mac

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Requirements

Create a file named:

```text
requirements.txt
```

Add:

```text
Flask
Werkzeug
python-dotenv
```

Install:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a file named:

```text
.env
```

Example:

```env
SECRET_KEY=your_secret_key_here

SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
```

---

## Gmail App Password Setup

1. Enable 2-Step Verification in Google Account.
2. Open Google App Passwords.
3. Create a new App Password.
4. Copy the generated password.
5. Use it as:

```env
SENDER_PASSWORD=generated_app_password
```

---

## Running the Project

```bash
python app.py
```

Server starts on:

```text
http://127.0.0.1:5000
```

---

## Demo Mode

If:

```env
SENDER_EMAIL=
SENDER_PASSWORD=
```

are not configured, the application automatically enters Demo Mode.

OTP will be printed in the terminal instead of sending an email.

Example:

```text
==================================================
DEMO MODE: EMAIL NOT CONFIGURED
OTP for user@example.com is: 123456
==================================================
```

---

## Default Database

The application automatically creates:

```text
users.db
```

with table:

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
```

---

## Workflow

### Registration

User → Register → Account Created

### Login

User → Login → Dashboard

### Forgot Password

User → Enter Email → OTP Generated

### OTP Verification

User → Enter OTP → Verified

### Password Reset

User → New Password → Password Updated

### Dashboard

User → Logged In Session

---

## Security Notes

* Passwords are hashed before storage.
* Plain-text passwords are never saved.
* Sessions are used for authentication.
* Email uniqueness is enforced.
* OTP is generated dynamically.

---

## Author

Sonu Tiwari

BCA Student | Python & Web Development Enthusiast
