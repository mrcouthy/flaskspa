from flask import render_template
from app import app # or from . import app if preferred

@app.route('/')
@app.route('/index') # Optional: alias for convenience
def index(): # Ensure function is named 'index'
    return render_template('index.html', title='Home')
