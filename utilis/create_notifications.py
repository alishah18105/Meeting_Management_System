from datetime import datetime
from models import Notification, db


def create_notification(user_id, meeting_id, message):
    notification = Notification(
        user_id=user_id,
        meeting_id=meeting_id,
        message=message,
        created_at=datetime.utcnow(),
        is_read=False
    )
    db.session.add(notification)
    db.session.commit()