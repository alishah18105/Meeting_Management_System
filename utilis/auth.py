from flask import flash
from functools import wraps
from flask import redirect, session, url_for


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login first to access this page.", "warning")
            return redirect(url_for('loginPage'))
        return f(*args, **kwargs)
    return decorated_function