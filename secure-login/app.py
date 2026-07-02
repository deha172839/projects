import os
import re
import sqlite3
from datetime import timedelta
from functools import wraps

import bcrypt
import pyotp
import qrcode
import qrcode.image.svg
from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, g, abort
)
from flask_wtf.csrf import CSRFProtect
from io import BytesIO
from base64 import b64encode

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get(
    'SECRET_KEY',
    'change-this-to-a-very-long-random-string-in-production'
)
app.permanent_session_lifetime = timedelta(minutes=30)

# CSRF protection
csrf = CSRFProtect(app)

# ─── Database Helpers ─────────────────────────────────────────────

DATABASE = os.path.join(os.path.dirname(__file__), 'users.db')


def get_db():
    """Get a database connection for the current request."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA foreign_keys=ON")
    return db


def init_db():
    """Create tables if they don't exist."""
    with app.app_context():
        db = get_db()
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT    NOT NULL UNIQUE,
                email       TEXT    NOT NULL UNIQUE,
                password    TEXT    NOT NULL,
                totp_secret TEXT    DEFAULT NULL,
                totp_enabled INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                token       TEXT    NOT NULL UNIQUE,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        db.commit()


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# ─── Input Validation ────────────────────────────────────────────

USERNAME_RE = re.compile(r'^[a-zA-Z0-9_]{3,30}$')
EMAIL_RE   = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


def validate_username(username):
    """Return True if username is valid."""
    return bool(USERNAME_RE.match(username))


def validate_email(email):
    """Return True if email is valid."""
    return bool(EMAIL_RE.match(email))


def validate_password(password):
    """
    Password policy:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-]', password):
        return False, "Password must contain at least one special character."
    return True, ""


def sanitise_input(value):
    """Strip whitespace and remove null bytes."""
    if isinstance(value, str):
        return value.strip().replace('\x00', '')
    return value

# ─── Authentication Helpers ──────────────────────────────────────

def generate_session_token():
    """Generate a cryptographically random session token."""
    return os.urandom(32).hex()


def login_required(f):
    """Decorator to protect routes that require authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def get_current_user():
    """Return the user Row object for the logged-in user, or None."""
    user_id = session.get('user_id')
    if user_id is None:
        return None
    db = get_db()
    user = db.execute(
        "SELECT id, username, email, totp_enabled FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    return user

# ─── Routes ───────────────────────────────────────────────────────

@app.route('/')
def index():
    return redirect(url_for('dashboard' if 'user_id' in session else 'login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = sanitise_input(request.form.get('username', ''))
        email    = sanitise_input(request.form.get('email', ''))
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        # --- Server-side validation ---
        if not username or not email or not password or not confirm:
            flash("All fields are required.", "danger")
            return render_template('register.html')

        if not validate_username(username):
            flash("Username must be 3–30 characters (letters, digits, underscores only).", "danger")
            return render_template('register.html')

        if not validate_email(email):
            flash("Please enter a valid email address.", "danger")
            return render_template('register.html')

        valid_pw, pw_msg = validate_password(password)
        if not valid_pw:
            flash(pw_msg, "danger")
            return render_template('register.html')

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template('register.html')

        # --- Check for existing users ---
        db = get_db()
        existing = db.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (username, email)
        ).fetchone()
        if existing:
            flash("Username or email already taken.", "danger")
            return render_template('register.html')

        # --- Hash password with bcrypt (cost factor 12) ---
        hashed = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt(rounds=12)
        ).decode('utf-8')

        # --- Insert new user (parameterised query = SQLi protection) ---
        db.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed)
        )
        db.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = sanitise_input(request.form.get('username', ''))
        password = request.form.get('password', '')
        totp_code = sanitise_input(request.form.get('totp_code', ''))

        if not username or not password:
            flash("Username and password are required.", "danger")
            return render_template('login.html')

        db = get_db()
        # Parameterised query prevents SQL injection
        user = db.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if user is None:
            # Use identical timing to avoid user enumeration
            bcrypt.checkpw(
                b"dummy",
                b"$2b$12$" + b"x" * 53
            )
            flash("Invalid username or password.", "danger")
            return render_template('login.html')

        # Verify password
        if not bcrypt.checkpw(
            password.encode('utf-8'),
            user['password'].encode('utf-8')
        ):
            flash("Invalid username or password.", "danger")
            return render_template('login.html')

        # --- 2FA check ---
        if user['totp_enabled']:
            if not user['totp_secret']:
                flash(
                    "Two-factor authentication is misconfigured for this account. "
                    "Please contact support or reset your 2FA settings.",
                    "warning"
                )
                return render_template('login.html', username=username)
            if not totp_code:
                # Show TOTP field (re-render with flag)
                return render_template('login.html', totp_required=True, username=username)
            totp = pyotp.TOTP(user['totp_secret'])
            if not totp.verify(totp_code, valid_window=1):
                flash("Invalid two-factor authentication code.", "danger")
                return render_template('login.html', totp_required=True, username=username)

        # --- Create session ---
        session.permanent = True
        session['user_id'] = user['id']
        session['username'] = user['username']

        # Store session token in DB for server-side tracking
        token = generate_session_token()
        db.execute(
            "INSERT INTO sessions (user_id, token) VALUES (?, ?)",
            (user['id'], token)
        )
        db.commit()

        flash(f"Welcome back, {user['username']}!", "success")
        return redirect(url_for('dashboard'))

    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    return render_template('dashboard.html', user=user)


@app.route('/logout')
def logout():
    # Clear server-side session record
    if 'user_id' in session:
        db = get_db()
        db.execute(
            "DELETE FROM sessions WHERE user_id = ?",
            (session['user_id'],)
        )
        db.commit()
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


# ─── 2FA Routes ──────────────────────────────────────────────────

@app.route('/setup-2fa', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    user = get_current_user()
    db = get_db()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'enable':
            # Verify current password
            stored = db.execute(
                "SELECT password FROM users WHERE id = ?",
                (user['id'],)
            ).fetchone()['password']

            password = request.form.get('password', '')
            if not bcrypt.checkpw(password.encode('utf-8'), stored.encode('utf-8')):
                flash("Password is incorrect.", "danger")
                return redirect(url_for('setup_2fa'))

            # Generate TOTP secret
            secret = pyotp.random_base32()
            db.execute(
                "UPDATE users SET totp_secret = ?, totp_enabled = 1 WHERE id = ?",
                (secret, user['id'])
            )
            db.commit()
            flash("Two-factor authentication has been enabled.", "success")
            return redirect(url_for('setup_2fa'))

        elif action == 'disable':
            db.execute(
                "UPDATE users SET totp_secret = NULL, totp_enabled = 0 WHERE id = ?",
                (user['id'],)
            )
            db.commit()
            flash("Two-factor authentication has been disabled.", "info")
            return redirect(url_for('setup_2fa'))

        elif action == 'verify':
            code = sanitise_input(request.form.get('code', ''))
            stored_secret = db.execute(
                "SELECT totp_secret FROM users WHERE id = ?",
                (user['id'],)
            ).fetchone()['totp_secret']

            if not stored_secret:
                flash("2FA is not set up.", "warning")
                return redirect(url_for('setup_2fa'))

            totp = pyotp.TOTP(stored_secret)
            if totp.verify(code, valid_window=1):
                flash("Code verified successfully!", "success")
            else:
                flash("Invalid code. Try again.", "danger")
            return redirect(url_for('setup_2fa'))

    # GET: show 2FA status and optionally provisioning info
    stored = db.execute(
        "SELECT totp_secret, totp_enabled FROM users WHERE id = ?",
        (user['id'],)
    ).fetchone()

    qr_uri = None
    if stored['totp_enabled'] and stored['totp_secret']:
        # Generate provisioning URI and QR code
        totp = pyotp.TOTP(stored['totp_secret'])
        provisioning_uri = totp.provisioning_uri(
            name=user['email'],
            issuer_name="SecureLoginApp"
        )

        # Render QR as in-memory SVG
        img = qrcode.make(provisioning_uri, image_factory=qrcode.image.svg.SvgImage)
        buf = BytesIO()
        img.save(buf)
        qr_uri = "data:image/svg+xml;base64," + b64encode(buf.getvalue()).decode()

    return render_template(
        'setup_2fa.html',
        user=user,
        totp_enabled=bool(stored['totp_enabled']),
        qr_uri=qr_uri
    )


# ─── Entry Point ─────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0', port=5000)