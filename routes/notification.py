from flask import Blueprint, redirect, render_template, session, url_for, request
from models import Notification,db
from routes.todo import login_required


notification_bp = Blueprint('notification', __name__,template_folder="../templates")

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

@notification_bp.route('/notification/read/<int:notification_id>')
@login_required
def notification_read(notification_id):
    user_id = session['user_id']
    notification = Notification.query.filter_by(notification_id=notification_id, user_id=user_id).first()

    if notification:
        notification.is_read = True
        db.session.commit()

    next_url = request.referrer or url_for('dashboard.home')
    return redirect(next_url)
