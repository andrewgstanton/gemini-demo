from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import get_db_connection, init_db
import hashlib
import sqlite3 # Import sqlite3 for IntegrityError

app = Flask(__name__)
app.secret_key = 'your_super_secret_key' # CHANGE THIS TO A STRONG, UNIQUE KEY IN PRODUCTION!

# Initialize the database when the app starts
with app.app_context():
    init_db()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(hashed_password, user_password):
    return hashed_password == hashlib.sha256(user_password.encode()).hexdigest()

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30) # Example: session lasts 30 minutes

from datetime import timedelta

@app.route('/register', methods=('GET', 'POST'))
def register():
    if 'user_id' in session:
        return redirect(url_for('notes')) # If already logged in, redirect to notes

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password(password)

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                         (username, hashed_password))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose a different one.', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if 'user_id' in session:
        return redirect(url_for('notes')) # If already logged in, redirect to notes

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('notes'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/notes', methods=('GET',))
def notes():
    if 'user_id' not in session:
        flash('Please log in to view your notes.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    user_notes = conn.execute("SELECT * FROM notes WHERE user_id = ? ORDER BY id DESC", (session['user_id'],)).fetchall()
    conn.close()
    return render_template('notes.html', notes=user_notes)

@app.route('/add_note', methods=('GET', 'POST'))
def add_note():
    if 'user_id' not in session:
        flash('Please log in to add notes.', 'warning')
        return redirect(url_for('login'))

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
def edit_note(note_id):
    if 'user_id' not in session:
        flash('Please log in to edit notes.', 'warning')
        return redirect(url_for('login'))

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
def delete_note(note_id):
    if 'user_id' not in session:
        flash('Please log in to delete notes.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    # Ensure the user owns the note they are trying to delete
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