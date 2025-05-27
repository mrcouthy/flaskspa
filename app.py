from flask import Flask, render_template, flash, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, roles_required, current_user, roles_accepted
from flask_security.recoverable import send_reset_password_instructions
from flask_mail import Mail
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectMultipleField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email
# from wtforms.fields import PasswordField # This was for older Flask-WTF, PasswordField is now in wtforms directly

# Basic App Configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-for-dev' # Replace with a real secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail Configuration (for console output)
app.config['MAIL_SERVER'] = 'localhost'
app.config['MAIL_PORT'] = 1025
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = None
app.config['MAIL_PASSWORD'] = None
app.config['MAIL_DEFAULT_SENDER'] = 'noreply@example.com'

# Flask-Security-Too Configuration
app.config['SECURITY_PASSWORD_SALT'] = 'super-secret-salt-for-dev' # Replace with a real salt
app.config['SECURITY_REGISTERABLE'] = False # Disable self-registration
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = ['email'] # Use email as username
app.config['SECURITY_POST_LOGIN_VIEW'] = '/'
app.config['SECURITY_POST_LOGOUT_VIEW'] = '/'
app.config['SECURITY_EMAIL_SENDER'] = 'noreply@example.com' # For Flask-Security-Too emails
# SECURITY_RESET_URL and SECURITY_RESET_PASSWORD_URL default to /reset and /reset/<token>

# Initialize SQLAlchemy and Mail
db = SQLAlchemy(app)
mail = Mail(app)

# Define Models (Role and User are already defined below, ensuring imports are correct)
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False) # Required for Flask-Security-Too v5+
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
# 'security' variable will be initialized after form and models are defined.

# Forms
class AddUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    # Choices are set dynamically in the route
    roles = SelectMultipleField('Roles', coerce=int, validate_choice=False)
    active = BooleanField('Active', default=True)
    submit = SubmitField('Create User')

class EditUserRolesForm(FlaskForm):
    # Choices are set dynamically in the route
    roles = SelectMultipleField('Roles', coerce=int, validate_choice=False)
    submit = SubmitField('Update Roles')

security = Security(app, user_datastore) # Initialize security after models and forms that might be needed by security

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/content_dashboard')
@roles_accepted('editor', 'admin')
def content_dashboard():
    return render_template('content_dashboard.html')

@app.route('/view_content')
@roles_accepted('viewer', 'editor', 'admin')
def view_content():
    return render_template('view_content.html')

@app.route('/admin/dashboard')
@roles_required('admin')
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/admin/add_user', methods=['GET', 'POST'])
@roles_required('admin')
def add_user():
    form = AddUserForm()
    # Populate roles choices dynamically
    form.roles.choices = [(role.id, role.name) for role in Role.query.all()]

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        active = form.active.data
        role_ids = form.roles.data

        if user_datastore.find_user(email=email):
            flash(f"User with email {email} already exists.", 'danger')
        else:
            selected_roles = [user_datastore.find_role(id=role_id) for role_id in role_ids]
            # Filter out None if a role_id was invalid, though validate_choice=False might allow non-existent ones
            selected_roles = [role for role in selected_roles if role]
            
            user_datastore.create_user(
                email=email,
                password=password, # Flask-Security-Too will hash this
                active=active,
                roles=selected_roles
            )
            db.session.commit()
            flash(f"User {email} created successfully!", 'success')
            return redirect(url_for('add_user')) # Redirect to clear form or to a user list
    
    return render_template('admin/add_user.html', form=form)

@app.route('/admin/users')
@roles_required('admin')
def user_management():
    users = User.query.all()
    return render_template('admin/user_management.html', users=users)

@app.route('/admin/user/<int:user_id>/edit_roles', methods=['GET', 'POST'])
@roles_required('admin')
def edit_user_roles(user_id):
    user = user_datastore.get_user(user_id)
    if not user:
        flash(f"User with ID {user_id} not found.", "danger")
        return redirect(url_for('user_management'))

    form = EditUserRolesForm()
    # Populate roles choices dynamically
    form.roles.choices = [(role.id, role.name) for role in Role.query.all()]

    if form.validate_on_submit():
        # Clear existing roles
        for role in list(user.roles): # Iterate over a copy for safe removal
            user_datastore.remove_role_from_user(user, role)
        
        # Add newly selected roles
        for role_id in form.roles.data:
            role_obj = user_datastore.find_role(id=role_id)
            if role_obj:
                user_datastore.add_role_to_user(user, role_obj)
        
        db.session.commit()
        flash(f"Roles for {user.email} updated successfully.", 'success')
        return redirect(url_for('user_management'))
    elif not form.is_submitted(): # Populate form with current roles on GET request
        form.roles.data = [role.id for role in user.roles]

    return render_template('admin/edit_user_roles.html', form=form, user=user)

@app.route('/admin/user/<int:user_id>/reset_password', methods=['POST'])
@roles_required('admin')
def admin_reset_password(user_id):
    user = user_datastore.get_user(user_id)
    if not user:
        flash(f"User with ID {user_id} not found.", "danger")
        return redirect(url_for('user_management')) # Or abort(404)
    
    # This uses Flask-Security-Too's mechanism, which should use the Mail setup
    # and configured templates (security/forgot_password.html, security/reset_password.html).
    # The actual email sending (or console output) happens via Flask-Mail.
    # The token generation and handling is done by Flask-Security-Too.
    send_reset_password_instructions(user)
    
    flash(f"Password reset instructions have been sent to {user.email}.", 'success')
    return redirect(url_for('user_management'))

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@roles_required('admin')
def delete_user(user_id):
    user_to_delete = User.query.get_or_404(user_id)

    if user_to_delete.id == current_user.id:
        flash("You cannot delete yourself.", "danger")
        return redirect(url_for('user_management'))

    # Check if the user has an 'admin' role - for additional safety, might prevent deletion of other admins
    # This is an optional, more advanced check. For now, we'll stick to the primary requirement.
    # if 'admin' in [role.name for role in user_to_delete.roles]:
    #     flash("Admin users cannot be deleted through this interface for safety.", "warning")
    #     return redirect(url_for('user_management'))

    email_copy = user_to_delete.email # For the flash message after deletion
    
    # Using user_datastore.delete_user is preferred as it might handle more FSecurity specific cleanups
    if user_datastore.delete_user(user_to_delete):
        db.session.commit() # Flask-Security-Too's delete_user might not commit by default
        flash(f"User {email_copy} has been deleted successfully.", 'success')
    else:
        # This case might be rare if get_or_404 already found the user
        flash(f"Error deleting user {email_copy}. User might not exist or other issue.", 'danger')
        
    return redirect(url_for('user_management'))


# A simple command to create the database tables and a default user/role
@app.cli.command("init-db")
def init_db_command():
    """Creates the database tables and default roles/users."""
    db.create_all()
    
    roles_to_create = {
        "admin": "Administrator",
        "editor": "Content Editor",
        "viewer": "Standard User/Viewer"
    }
    
    for role_name, role_description in roles_to_create.items():
        if not user_datastore.find_role(role_name):
            user_datastore.create_role(name=role_name, description=role_description)
            print(f"Role '{role_name}' created.")
            
    if not user_datastore.find_user(email="admin@example.com"):
        user_datastore.create_user(email="admin@example.com", password="password", roles=["admin"])
        print("Default admin user 'admin@example.com' created.")
        
    db.session.commit()
    print("Database initialization complete.")


if __name__ == '__main__':
    app.run(debug=True)
