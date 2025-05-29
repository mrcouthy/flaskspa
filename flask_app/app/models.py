from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# In-memory user store
users = {}  # Store user objects by id
users_by_username = {} # Store user_id by username for quick lookup

class User(UserMixin):
    def __init__(self, id, username, password, role='user'): # Added role
        self.id = id
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.role = role # Initialize role

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get(user_id):
        return users.get(user_id)

    @staticmethod
    def get_by_username(username):
        user_id = users_by_username.get(username)
        if user_id:
            return users.get(user_id)
        return None

    @staticmethod
    def create(username, password, role='user'): # Added role
        if username in users_by_username:
            return None # Username already exists
        # Ensure user_id is a string, as flask-login expects
        user_id = str(len(users) + 1)
        user = User(id=user_id, username=username, password=password, role=role) # Pass role
        users[user_id] = user
        users_by_username[username] = user_id
        return user

# Manually create an admin user for testing (adjust username/password as needed)
# This is a temporary measure for development.
if not User.get_by_username('admin'):
    admin_user = User.create(username='admin', password='adminpassword', role='admin')
    # The User.create method already adds the user to the 'users' and 'users_by_username' dicts.
