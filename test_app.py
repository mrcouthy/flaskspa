import os
import sqlite3
import pytest
from flask import session
from app import app, DATABASE, init_db, get_db # Assuming app.py has these

# Pytest fixture to set up the application context and test client
@pytest.fixture
def client():
    # Ensure a clean database for each test
    if os.path.exists(DATABASE):
        os.remove(DATABASE)

    # Configure the app for testing
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key' # Consistent secret key for testing sessions
    # Disable CSRF protection if any (not explicitly added, but good practice for testing forms)
    app.config['WTF_CSRF_ENABLED'] = False


    with app.app_context():
        init_db() # Initialize the database
        with app.test_client() as client:
            yield client

    # Clean up the database after tests run
    if os.path.exists(DATABASE):
        os.remove(DATABASE)

# Helper function to query the database directly
def query_db(query, args=(), one=False):
    with app.app_context():
        db = get_db()
        cur = db.execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv

# --- Test Functions ---

def test_flask_runnable(client):
    """1. Test if Flask is runnable (implicitly tested by client fixture)."""
    response = client.get('/')
    assert response.status_code == 200

def test_database_initialization(client):
    """2. Test database initialization."""
    # This is implicitly tested by the client fixture setup.
    # We can add an explicit check for tables.
    users_table = query_db("SELECT name FROM sqlite_master WHERE type='table' AND name='users';", one=True)
    feedback_table = query_db("SELECT name FROM sqlite_master WHERE type='table' AND name='feedback';", one=True)
    assert users_table is not None
    assert feedback_table is not None
    if os.path.exists(DATABASE): # Double check db file was created by init_db in fixture
        assert True
    else:
        assert False, "database.db was not created by init-db"


def test_user_registration(client):
    """3. Simulate User Registration."""
    # Attempt to register a new user
    response_register_new = client.post('/register', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)
    assert response_register_new.status_code == 200 # Should redirect to login (GET)
    assert b'Registration successful! Please log in.' in response_register_new.data
    assert b'Login' in response_register_new.data # Check if it landed on login page

    # Attempt to register the same user again
    response_register_duplicate = client.post('/register', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)
    assert response_register_duplicate.status_code == 200 # Stays on register page
    assert b'User testuser is already registered.' in response_register_duplicate.data
    assert b'Register' in response_register_duplicate.data # Check if it stayed on register page

def test_user_login_logout_and_login_count(client):
    """4. Simulate User Login, Logout, and check login count."""
    # First, register the user for login tests
    client.post('/register', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)

    # Attempt to log in with incorrect credentials
    response_login_incorrect = client.post('/login', data={
        'username': 'testuser',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert response_login_incorrect.status_code == 200 # Stays on login page
    assert b'Invalid username or password.' in response_login_incorrect.data
    assert b'Login' in response_login_incorrect.data

    # Attempt to log in with correct credentials
    response_login_correct = client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)
    assert response_login_correct.status_code == 200 # Redirects to home
    assert b'Logged in successfully!' in response_login_correct.data
    assert b'Welcome, testuser!' in response_login_correct.data # On homepage

    # Verify login count is 1
    user = query_db('SELECT * FROM users WHERE username = ?', ('testuser',), one=True)
    assert user is not None
    assert user['login_count'] == 1

    # Logout
    response_logout = client.get('/logout', follow_redirects=True)
    assert response_logout.status_code == 200 # Redirects to home
    assert b'You have been logged out.' in response_logout.data
    assert b'<p>Please <a href="/login">log in</a> or <a href="/register">register</a>.</p>' in response_logout.data # On homepage, not logged in

    # Log in again
    response_login_again = client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)
    assert response_login_again.status_code == 200
    assert b'Logged in successfully!' in response_login_again.data

    # Verify login count is 2
    user_after_relogin = query_db('SELECT * FROM users WHERE username = ?', ('testuser',), one=True)
    assert user_after_relogin is not None
    assert user_after_relogin['login_count'] == 2

def test_feedback_submission(client):
    """5. Simulate Feedback Submission."""
    # Attempt to access /feedback without being logged in
    response_feedback_unauth = client.get('/feedback', follow_redirects=True)
    assert response_feedback_unauth.status_code == 200 # Redirects to login
    assert b'Please log in to provide feedback.' in response_feedback_unauth.data
    assert b'Login' in response_feedback_unauth.data # On login page

    # Register and Log in as 'testuser'
    client.post('/register', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)
    client.post('/login', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)

    # Attempt to submit feedback
    feedback_text = "This is a test feedback."
    response_submit_feedback = client.post('/feedback', data={
        'feedback_text': feedback_text
    }, follow_redirects=True)
    assert response_submit_feedback.status_code == 200 # Redirects to home
    assert b'Thank you for your feedback!' in response_submit_feedback.data
    assert b'Welcome, testuser!' in response_submit_feedback.data # On homepage

    # Verify feedback is stored in the database
    user = query_db('SELECT id FROM users WHERE username = ?', ('testuser',), one=True)
    assert user is not None
    feedback_entry = query_db('SELECT * FROM feedback WHERE user_id = ? AND feedback_text = ?',
                              (user['id'], feedback_text), one=True)
    assert feedback_entry is not None
    assert feedback_entry['feedback_text'] == feedback_text

def test_logout_and_restricted_access(client):
    """6. Simulate Logout and check restricted access."""
    # Register and Log in
    client.post('/register', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)
    client.post('/login', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)

    # Logout
    response_logout = client.get('/logout', follow_redirects=True)
    assert response_logout.status_code == 200
    assert b'You have been logged out.' in response_logout.data
    assert b'<p>Please <a href="/login">log in</a> or <a href="/register">register</a>.</p>' in response_logout.data # On homepage, not logged in

    # Attempt to access /feedback again
    response_feedback_after_logout = client.get('/feedback', follow_redirects=True)
    assert response_feedback_after_logout.status_code == 200 # Redirects to login
    assert b'Please log in to provide feedback.' in response_feedback_after_logout.data
    assert b'Login' in response_feedback_after_logout.data # On login page

# To run these tests, one would typically use `pytest` in the terminal
# For example: `python -m pytest test_app.py` or simply `pytest`
# Ensure pytest is installed: `pip install pytest`
# The print statements for flask runnable are not part of the script,
# as flask run is a manual command. The test client implicitly tests runnability.
# The database deletion and init-db is handled by the fixture.
# The report will be generated based on the pytest output.
#
# For the `flask init-db` command, the test fixture runs `init_db()`
# which is the Python function that `flask init-db` calls.
# So, that part of the requirement is covered.
#
# The script does not use `requests` but uses `app.test_client()` as preferred.
# Session handling is managed automatically by the test client.
# Checks for status codes, redirection, and key phrases are included.
# Direct database checks are performed using the `query_db` helper.
#
# A slight modification is needed for app.py to ensure get_db() works outside request context
# for query_db helper or that query_db always uses app_context.
# The current query_db uses `with app.app_context():` so it should be fine.
#
# Also, the `DATABASE` path in `app.py` is `os.path.join(app.root_path, 'database.db')`.
# The `test_app.py` script should correctly locate this.
# The `DATABASE` import from `app` should provide the correct path.
#
# One final check: `init_db` in `app.py` uses `app.open_resource('schema.sql')`.
# This assumes `schema.sql` is in the application root's "resource" folder,
# or just the root if not a package. Given `schema.sql` is in the root, this is fine.
#
# The fixture `client` ensures `init_db()` is called, which in turn executes `schema.sql`.
# So, step 2 about `flask init-db` is covered.
# Step 1 "python -m flask run" is a manual command, the tests ensure the app *could* be run.
# The script is now ready.
# I should ensure `app.secret_key` is also set for testing if not already.
# Added `app.config['SECRET_KEY']` in the fixture for robust session testing.
# Added a check for database file creation in `test_database_initialization`.
# Flask's test client `follow_redirects=True` is very helpful for testing flows.
# Assertions for being on the correct page after redirects are added.
# (e.g. checking for "Login" in response.data after redirect to login page).
#
# The task asks to "report the results". This script is designed to be run by pytest,
# which will generate a detailed report of pass/fail for each test function.
# I will then summarize this pytest output in the subtask report.
#
# I need to ensure that `app.py` does not call `app.run()` when imported.
# The `if __name__ == '__main__': app.run(debug=True)` structure in `app.py` handles this.
# The test script imports `app` from `app.py`.
#
# The path to `schema.sql` in `init_db()` is `app.open_resource('schema.sql')`.
# If `app.py` is in the root, and `schema.sql` is in the root, this should work.
# `app.root_path` is the directory where `app.py` is.
# `open_resource` opens a resource from the application's resource folder,
# which by default is the application's root path if it's not a package.
# This seems correct.

# The test file is complete.
# The next step would be to run this with pytest.
# (End of script)
