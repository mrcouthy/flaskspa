import sqlite3
import os
from flask import Flask, render_template, g, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import click # Import click for CLI commands

app = Flask(__name__, instance_relative_config=True) # Enable instance folder
app.secret_key = os.urandom(24) # Needed for flash messages

# The instance folder is not used for the database in this setup,
# so the try-except block for creating it can be removed.
# If other parts of the app were to use the instance folder,
# os.makedirs(app.instance_path, exist_ok=True) would be appropriate.

DATABASE = os.path.join(app.root_path, 'database.db') # Place DB in project root

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row # Access columns by name
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        # schema.sql is in the root directory (same as app.py)
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.cli.command('init-db')
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

@app.route('/')
def home():
    # Example: Query users to test (optional)
    # try:
    #     db = get_db()
    #     cur = db.execute('SELECT * FROM users')
    #     users = cur.fetchall()
    #     print(f"Users: {users}")
    # except sqlite3.OperationalError as e:
    #     print(f"Error querying users: {e}. Did you run 'flask init-db'?")
    return render_template('index.html')

if __name__ == '__main__':
    # Ensure the DB is initialized if running directly (for dev convenience)
    # This is not strictly necessary if you always use 'flask init-db'
    # with app.app_context():
    #    if not os.path.exists(DATABASE):
    #        init_db()
    #        print("Database initialized on startup.")
    app.run(debug=True)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        
        if error is None:
            try:
                # Check if username already exists
                user = db.execute(
                    'SELECT id FROM users WHERE username = ?', (username,)
                ).fetchone()

                if user is not None:
                    error = f"User {username} is already registered."
                else:
                    # Insert new user
                    db.execute(
                        'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                        (username, generate_password_hash(password))
                    )
                    db.commit()
                    flash('Registration successful! Please log in.', 'success')
                    return redirect(url_for('login'))
            except sqlite3.IntegrityError: # Should be caught by the check above, but as a fallback
                error = f"User {username} is already registered."
            except Exception as e:
                error = f"An error occurred: {e}"

        if error:
            flash(error, 'danger')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Invalid username or password.'
        elif not check_password_hash(user['password_hash'], password):
            error = 'Invalid username or password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            
            # Increment login_count
            new_login_count = (user['login_count'] or 0) + 1
            db.execute(
                'UPDATE users SET login_count = ? WHERE id = ?',
                (new_login_count, user['id'])
            )
            db.commit()
            
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        
        flash(error, 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.context_processor
def inject_user():
    user_id = session.get('user_id')
    if user_id:
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        return dict(current_user=user)
    return dict(current_user=None)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'user_id' not in session:
        flash('Please log in to provide feedback.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        feedback_text = request.form['feedback_text']
        user_id = session['user_id']
        error = None

        if not feedback_text:
            error = 'Feedback text cannot be empty.'
        
        if error is None:
            try:
                db = get_db()
                db.execute(
                    'INSERT INTO feedback (user_id, feedback_text) VALUES (?, ?)',
                    (user_id, feedback_text)
                )
                db.commit()
                flash('Thank you for your feedback!', 'success')
                return redirect(url_for('home')) # Or url_for('feedback')
            except Exception as e:
                error = f"An error occurred while submitting your feedback: {e}"
        
        if error:
            flash(error, 'danger')

    return render_template('feedback.html')
