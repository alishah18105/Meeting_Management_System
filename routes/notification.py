from flask import Blueprint, render_template, session
from utilis.auth import login_required
from models import Notification,db


notification_bp = Blueprint('notificataion', __name__,template_folder="../templates")

@notification_bp.route('/notifications')
@login_required
def notifications():
    user_id = session['user_id']
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()

    # Mark all as read
    for n in notifications:
        n.is_read = True
    db.session.commit()

    unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()

    return render_template('notifications.html', notifications=notifications, unread_count=unread_count)
