from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from werkzeug.security import generate_password_hash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from utilis.auth import login_required

settings_bp = Blueprint('settings', __name__, template_folder="../templates")

@settings_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    user_id = session.get("user_id")
    user = User.query.get(user_id)

    if request.method == 'POST':
        new_name = request.form.get("name")
        new_email = request.form.get("email")
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")

        if new_name:
            user.name = new_name
        if new_email:
            user.email = new_email

        if old_password and new_password:
            if check_password_hash(user.password, old_password):
                user.password = generate_password_hash(new_password)
            else:
                flash("Old password is incorrect!", "danger")
                return redirect(url_for('settings.settings'))

        db.session.commit()
        flash("Account settings updated successfully!", "success")
        return redirect(url_for('settings.settings'))

    return render_template('settings.html', user=user)
