from flask import Blueprint, render_template
from flask_login import login_required # Ensure this is present
from app.auth.decorators import admin_required # Import the new decorator

sample_module2_bp = Blueprint(
    'sample_module2',
    __name__,
    template_folder='templates',
    static_folder='static' # Kept as is
)

@sample_module2_bp.route('/greet')
@login_required # Users must be logged in
@admin_required # And must be admin
def greet():
    return render_template('sample_module2_page.html')
