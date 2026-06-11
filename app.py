from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import random
import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------------------
# LOAD ENV VARIABLES
# ---------------------------
load_dotenv()

# ---------------------------
# FLASK APP CONFIG
# ---------------------------
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key_change_this")

# ---------------------------
# EMAIL CONFIG (OPTIONAL)
# ---------------------------
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

# ---------------------------
# DATABASE SETUP
# ---------------------------
DB_NAME = "users.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user


def create_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)

    try:
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, hashed_password)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print("Create User Error:", e)
        return False
    finally:
        conn.close()


def update_password(email, new_password):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = generate_password_hash(new_password)

    try:
        cursor.execute(
            "UPDATE users SET password = ? WHERE email = ?",
            (hashed_password, email)
        )
        conn.commit()
        return True
    except Exception as e:
        print("Update Password Error:", e)
        return False
    finally:
        conn.close()


# ---------------------------
# EMAIL OTP SEND FUNCTION
# ---------------------------
def send_otp_email(receiver_email, otp):
    """
    If email credentials exist -> send real email
    If not -> print OTP in terminal (demo/dev mode)
    """
    # DEMO MODE (no .env setup)
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("\n" + "=" * 50)
        print("DEMO MODE: EMAIL NOT CONFIGURED")
        print(f"OTP for {receiver_email} is: {otp}")
        print("=" * 50 + "\n")
        return True

    # REAL EMAIL MODE
    try:
        subject = "Your Password Reset OTP"
        body = f"Your OTP for password reset is: {otp}"

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = receiver_email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()

        print("OTP Email Sent Successfully")
        return True

    except Exception as e:
        print("Email Error:", e)
        return False


# ---------------------------
# ROUTES
# ---------------------------

# HOME
@app.route("/")
def home():
    if "user_email" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Email and password are required!")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters!")
            return redirect(url_for("register"))

        if get_user_by_email(email):
            flash("Email already registered!")
            return redirect(url_for("register"))

        if create_user(email, password):
            flash("Registration successful! Please login.")
            return redirect(url_for("login"))
        else:
            flash("Registration failed!")
            return redirect(url_for("register"))

    return render_template("register.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Email and password are required!")
            return redirect(url_for("login"))

        user = get_user_by_email(email)

        if user and check_password_hash(user[2], password):
            session["user_email"] = user[1]
            flash("Login successful!")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password!")
            return redirect(url_for("login"))

    return render_template("login.html")


# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user_email" not in session:
        flash("Please login first!")
        return redirect(url_for("login"))

    return render_template("dashboard.html", email=session["user_email"])


# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!")
    return redirect(url_for("login"))


# FORGOT PASSWORD - SEND OTP
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        if not email:
            flash("Please enter your email!")
            return redirect(url_for("forgot_password"))

        user = get_user_by_email(email)
        if not user:
            flash("Email not found!")
            return redirect(url_for("forgot_password"))

        otp = str(random.randint(100000, 999999))

        session["reset_email"] = email
        session["reset_otp"] = otp

        if send_otp_email(email, otp):
            if not SENDER_EMAIL or not SENDER_PASSWORD:
                flash("OTP generated in terminal (demo mode). Check VS Code terminal.")
            else:
                flash("OTP sent to your email!")
            return redirect(url_for("verify_otp"))
        else:
            flash("Failed to send OTP. Check email settings.")
            return redirect(url_for("forgot_password"))

    return render_template("forgot_password.html")


# VERIFY OTP
@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if "reset_email" not in session:
        flash("Please request OTP first!")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        entered_otp = request.form.get("otp", "").strip()
        saved_otp = session.get("reset_otp")

        if not entered_otp:
            flash("Please enter OTP!")
            return redirect(url_for("verify_otp"))

        if entered_otp == saved_otp:
            flash("OTP verified successfully!")
            return redirect(url_for("reset_password"))
        else:
            flash("Invalid OTP!")
            return redirect(url_for("verify_otp"))

    return render_template("verify_otp.html")


# RESET PASSWORD
@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if "reset_email" not in session:
        flash("Please verify OTP first!")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("password", "").strip()
        email = session["reset_email"]

        if not new_password:
            flash("Please enter new password!")
            return redirect(url_for("reset_password"))

        if len(new_password) < 6:
            flash("Password must be at least 6 characters!")
            return redirect(url_for("reset_password"))

        success = update_password(email, new_password)

        if not success:
            flash("Failed to reset password!")
            return redirect(url_for("reset_password"))

        # Auto login after reset
        session["user_email"] = email

        # Clear reset session
        session.pop("reset_email", None)
        session.pop("reset_otp", None)

        flash("Password reset successful! You are now logged in.")
        return redirect(url_for("dashboard"))

    return render_template("reset_password.html")


# ---------------------------
# RUN APP
# ---------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)