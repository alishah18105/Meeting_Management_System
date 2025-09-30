from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ----------------------
# Users Table
# ----------------------
class User(db.Model):
    __tablename__ = "users"
    
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    # Relationships
    organizer = db.relationship("Organizer", back_populates="user", uselist=False, cascade="all, delete")
    participants = db.relationship("Participant", back_populates="user", cascade="all, delete")
    notifications = db.relationship("Notification", back_populates="user", cascade="all, delete")

    def __repr__(self):
        return f"<User {self.name}>"


# ----------------------
# Rooms Table
# ----------------------
class Room(db.Model):
    __tablename__ = "rooms"
    
    room_id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(100), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    meetings = db.relationship("Meeting", back_populates="room", cascade="all, delete")

    def __repr__(self):
        return f"<Room {self.room_name}>"


# ----------------------
# Organizers Table
# ----------------------
class Organizer(db.Model):
    __tablename__ = "organizers"
    
    organizer_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE", onupdate="CASCADE"), unique=True, nullable=False)
    
    # Relationships
    user = db.relationship("User", back_populates="organizer")
    meetings = db.relationship("Meeting", back_populates="organizer", cascade="all, delete")

    def __repr__(self):
        return f"<Organizer user_id={self.user_id}>"


# ----------------------
# Meetings Table
# ----------------------
class Meeting(db.Model):
    __tablename__ = "meetings"
    
    meeting_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="Scheduled")
    organizer_id = db.Column(db.Integer, db.ForeignKey("organizers.organizer_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.room_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    
    # Relationships
    organizer = db.relationship("Organizer", back_populates="meetings")
    room = db.relationship("Room", back_populates="meetings")
    participants = db.relationship("Participant", back_populates="meeting", cascade="all, delete")
    notifications = db.relationship("Notification", back_populates="meeting", cascade="all, delete")


    def __repr__(self):
        return f"<Meeting {self.title}>"


# ----------------------
# Participants Table
# ----------------------
class Participant(db.Model):
    __tablename__ = "participants"
    
    participant_id = db.Column(db.Integer, primary_key=True)
    attendance_status = db.Column(db.String(20), default="invited")
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    meeting_id = db.Column(db.Integer, db.ForeignKey("meetings.meeting_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    
    # Relationships
    meeting = db.relationship("Meeting", back_populates="participants")
    user = db.relationship("User", back_populates="participants")

    def __repr__(self):
        return f"<Participant user_id={self.user_id} meeting_id={self.meeting_id}>"


# ----------------------
# Notifications Table
# ----------------------
class Notification(db.Model):
    __tablename__ = "notifications"
    
    notification_id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    meeting_id = db.Column(db.Integer, db.ForeignKey("meetings.meeting_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    
    # Relationships
    user = db.relationship("User", back_populates="notifications")
    meeting = db.relationship("Meeting", back_populates="notifications")

    def __repr__(self):
        return f"<Notification to user_id={self.user_id} meeting_id={self.meeting_id}>"
