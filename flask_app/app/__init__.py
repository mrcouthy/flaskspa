from flask import Flask
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from .models import User # Assuming User model is in models.py

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_very_secret_key_that_should_be_random_and_long' # Replace with a real secret key

# Initialize Flask-Bootstrap
Bootstrap(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
# login_view will be set after auth_bp is imported and registered.

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Import and register blueprints
from app.modules.sample_module1.routes import sample_module1_bp
from app.modules.sample_module2.routes import sample_module2_bp
from app.auth.routes import auth_bp # Import the auth blueprint

app.register_blueprint(sample_module1_bp, url_prefix='/mod1')
app.register_blueprint(sample_module2_bp, url_prefix='/mod2')
app.register_blueprint(auth_bp, url_prefix='/auth')

# Now set login_view, after auth_bp is registered.
login_manager.login_view = 'auth.login'

# Import main app routes last
from app import routes
