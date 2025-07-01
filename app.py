from flask import Flask, render_template, request, redirect, url_for, session, flash, current_app, g
from database import get_db_connection, init_db
import hashlib
import sqlite3
from flask_mail import Mail, Message # NEW: For sending emails
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature # NEW: For tokens
import os # NEW: To load environment variables
from dotenv import load_dotenv # NEW: To load .env file
from datetime import timedelta

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_super_secret_key_default') # Get from .env or use default

# Flask-Mail configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME') # Or a specific sender email

mail = Mail(app) # Initialize Flask-Mail

# Initialize the serializer for tokens
s = URLSafeTimedSerializer(app.secret_key)

# Initialize the database when the app starts
with app.app_context():
    init_db()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(hashed_password, user_password):
    return hashed_password == hashlib.sha256(user_password.encode()).hexdigest()

# Decorator to check if user is logged in and verified
def login_required_and_verified(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        
        conn = get_db_connection()
        user = conn.execute("SELECT verified FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        conn.close()

        if user and not user['verified']:
            flash('Your account is not verified. Please check your email for the verification link.', 'warning')
            return redirect(url_for('unconfirmed'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def load_user_status():
    g.user = None
    g.user_verified = False
    if 'user_id' in session:
        conn = get_db_connection()
        user_data = conn.execute("SELECT id, username, verified, email FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        conn.close()
        if user_data:
            g.user = user_data
            g.user_verified = user_data['verified']

# Add functools for the decorator
import functools

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)

# Function to send verification email
def send_verification_email(user_email, token):
    verification_link = url_for('verify_email', token=token, _external=True)
    msg = Message("Confirm Your Email Address for My Notes App",
                  recipients=[user_email])
    msg.html = render_template('verify_email.html', verification_link=verification_link)
    try:
        mail.send(msg)
        return True
    except Exception as e:
        app.logger.error(f"Failed to send email to {user_email}: {e}")
        return False

def login_required_and_verified(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))

        # Check g.user_verified set by load_user_status
        if not g.user_verified:
            flash('Your account is not verified. Please check your email for the verification link.', 'warning')
            return redirect(url_for('unconfirmed'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=('GET', 'POST'))
def register():
    if 'user_id' in session:
        return redirect(url_for('notes'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email'] # Get email
        password = request.form['password']
        hashed_password = hash_password(password)

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, email, password, verified) VALUES (?, ?, ?, ?)",
                         (username, email, hashed_password, 0)) # Set verified to 0 (False)
            conn.commit()

            # Generate token and send email
            token = s.dumps(email, salt='email-confirm')
            if send_verification_email(email, token):
                flash(f'Registration successful! A verification email has been sent to {email}. Please verify your account to log in.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Registration successful, but failed to send verification email. Please contact support.', 'danger')
                # Optionally, clean up the user if email sending is critical
                return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or Email already exists. Please choose a different one.', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if 'user_id' in session:
        return redirect(url_for('notes'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password(user['password'], password):
            if user['verified']: # Check if verified
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash('Logged in successfully!', 'success')
                return redirect(url_for('notes'))
            else:
                flash('Your account is not verified. Please check your email for the verification link.', 'warning')
                return redirect(url_for('unconfirmed')) # Redirect to a page explaining unconfirmed status
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# NEW Route for email verification
@app.route('/verify_email/<token>')
def verify_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600) # Token valid for 1 hour
    except SignatureExpired:
        flash('The verification link has expired. Please log in to resend the verification email.', 'danger')
        return redirect(url_for('login'))
    except BadTimeSignature:
        flash('The verification link is invalid. Please try again or contact support.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    if user:
        if not user['verified']:
            conn.execute("UPDATE users SET verified = 1 WHERE id = ?", (user['id'],))
            conn.commit()
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Your account has been successfully verified! You are now logged in.', 'success')
            conn.close()
            return redirect(url_for('notes'))
        else:
            flash('Your account has already been verified. Please log in.', 'info')
    else:
        flash('No user found with that email address.', 'danger')
    conn.close()
    return redirect(url_for('login'))

# NEW route for unconfirmed users
@app.route('/unconfirmed')
def unconfirmed(): # Removed @login_required_and_verified here, as this page *is* for unconfirmed users
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if g.user_verified: # If suddenly verified, redirect
        return redirect(url_for('notes'))

    # No database query needed here, as g.user_verified is set by before_request
    return render_template('unconfirmed.html')

# NEW route to resend verification email
@app.route('/resend_verification_email')
def resend_verification_email():
    if 'user_id' not in session:
        flash('Please log in to resend the verification email.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute("SELECT email, verified FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    conn.close()

    if user and not user['verified']:
        email = user['email']
        token = s.dumps(email, salt='email-confirm')
        if send_verification_email(email, token):
            flash(f'A new verification email has been sent to {email}. Please check your inbox.', 'success')
        else:
            flash('Failed to resend verification email. Please try again later or contact support.', 'danger')
    else:
        flash('Your account is already verified or no user found.', 'info')

    return redirect(url_for('unconfirmed')) # Stay on unconfirmed page

@app.route('/notes', methods=('GET',))
@login_required_and_verified # Protect this route
def notes():
    conn = get_db_connection()
    user_notes = conn.execute("SELECT * FROM notes WHERE user_id = ? ORDER BY id DESC", (session['user_id'],)).fetchall()
    conn.close()
    return render_template('notes.html', notes=user_notes)

@app.route('/add_note', methods=('GET', 'POST'))
@login_required_and_verified # Protect this route
def add_note():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = session['user_id']

        if not title:
            flash('Note title is required!', 'danger')
        else:
            conn = get_db_connection()
            conn.execute("INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)",
                         (user_id, title, content))
            conn.commit()
            conn.close()
            flash('Note added successfully!', 'success')
            return redirect(url_for('notes'))
    return render_template('add_note.html')

@app.route('/edit_note/<int:note_id>', methods=('GET', 'POST'))
@login_required_and_verified # Protect this route
def edit_note(note_id):
    conn = get_db_connection()
    note = conn.execute("SELECT * FROM notes WHERE id = ? AND user_id = ?",
                        (note_id, session['user_id'])).fetchone()

    if not note:
        flash('Note not found or you do not have permission to edit it.', 'danger')
        conn.close()
        return redirect(url_for('notes'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Note title is required!', 'danger')
        else:
            conn.execute("UPDATE notes SET title = ?, content = ? WHERE id = ?",
                         (title, content, note_id))
            conn.commit()
            flash('Note updated successfully!', 'success')
            conn.close()
            return redirect(url_for('notes'))
    conn.close()
    return render_template('edit_note.html', note=note)

@app.route('/delete_note/<int:note_id>', methods=('POST',))
@login_required_and_verified # Protect this route
def delete_note(note_id):
    conn = get_db_connection()
    note = conn.execute("SELECT id FROM notes WHERE id = ? AND user_id = ?",
                        (note_id, session['user_id'])).fetchone()

    if note:
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        flash('Note deleted successfully!', 'success')
    else:
        flash('Note not found or you do not have permission to delete it.', 'danger')
    conn.close()
    return redirect(url_for('notes'))

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('notes'))
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True) # Set debug=False in a production environment