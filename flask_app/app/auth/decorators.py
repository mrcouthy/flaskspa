from functools import wraps
from flask import abort, redirect, url_for, flash, request # Added request for request.url
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            # If not authenticated, Flask-Login's @login_required usually handles this,
            # but good to have a check if this decorator is used independently.
            # Using request.url to redirect back to the originally requested page after login.
            return redirect(url_for('auth.login', next=request.url))
        
        # Using getattr for safety, though our User model should always have a role.
        if getattr(current_user, 'role', 'user') != 'admin':
            flash('You do not have permission to access this page. Admin access required.', 'danger')
            # Redirect to a general page or a specific 'unauthorized' page if you create one
            return redirect(url_for('index')) # Assuming 'index' is the main page route name
        return f(*args, **kwargs)
    return decorated_function
