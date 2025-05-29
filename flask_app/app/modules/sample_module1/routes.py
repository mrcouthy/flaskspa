from flask import Blueprint, render_template
from flask_login import login_required # Import

# Note: Using a unique name for the blueprint variable like 'sample_module1_bp'
sample_module1_bp = Blueprint(
    'sample_module1',
    __name__,
    template_folder='templates',
    static_folder='static' # if you plan to have static files for this module
)

@sample_module1_bp.route('/hello')
@login_required # Protect this route
def hello():
    return render_template('sample_module1_page.html')
