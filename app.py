from ctypes import cast
from datetime import datetime, timedelta
from email.mime import text
from operator import or_
import os
from flask import Flask, flash, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
from models import Meeting, Organizer, Participant, Room, db, User, Notification
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import redirect, session, url_for, flash
from routes.Calendar import calendar_bp 
from sqlalchemy import func, cast, Numeric, or_
from routes.todo import todo_bp
from routes.dashboard import dashboard_bp


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:ali@localhost:5432/meeting_systemdb"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.urandom(24)
app.register_blueprint(calendar_bp)
app.register_blueprint(todo_bp)
app.register_blueprint(dashboard_bp)
db.init_app(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login first to access this page.", "warning")
            return redirect(url_for('loginPage'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_notifications():
    if 'user_id' in session:
        user_id = session['user_id']
        notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(5).all()
        unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    else:
        notifications, unread_count = [], 0
    return dict(notifications=notifications, unread_count=unread_count)


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


@app.route('/notifications')
@login_required
def notifications():
    user_id = session['user_id']
    # Fetch latest 5 notifications for current user
    user_notifications = Notification.query.filter_by(user_id=user_id)\
        .order_by(Notification.created_at.desc())\
        .limit(5).all()

    # Count unread notifications
    unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()

    return render_template('notifications.html',notifications=user_notifications,unread_count=unread_count)




@app.route('/',methods=['GET', 'POST'] )
def signUpPage():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered. Redirecting to Login Screen.", "warning")
            return render_template('signup.html', redirect_to_login=True)

        else:
            user_details = User(
                name = name,
                email = email,
                password = hashed_password
            )
            db.session.add(user_details)
            db.session.commit()
            flash("Account created successfully! Please login.", "success")
            return redirect('/login')
    return render_template('signup.html')

@app.route('/login',methods=['GET', 'POST'] )
def loginPage():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']


        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.user_id
            session['user_name'] = user.name
            flash('Login successful!', 'success')
            return redirect('/home')
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')

@app.route('/home',methods=['GET', 'POST'] )
@login_required
def homePage():
    return render_template('menu.html')


@app.route('/instant_meeting', methods = ['GET', 'POST'])
def instant_meeting():
    if request.method == 'POST':
        title = request.form['title']
        room_id = request.form['room_id']
        description = request.form['description']
        status = "Ongoing"
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=4)  # For instant meetings, end time can be set later

        user_id = session['user_id']

        # Check if user is organizer
        organizer = Organizer.query.filter_by(user_id=user_id).first()
        if not organizer:
            organizer = Organizer(user_id=user_id)
            db.session.add(organizer)
            db.session.commit()

        # Create meeting
        meeting = Meeting(
            title=title,
            room_id=room_id,
            description=description,
            status=status,
            start_time=start_time,
            end_time=end_time,
            organizer_id=organizer.organizer_id
        )
        db.session.add(meeting)
        db.session.commit()
        return redirect('/meeting')

@app.route('/meeting', methods=['GET', 'POST'])
@login_required
def meeting():
    if request.method == 'POST':
        title = request.form['title']
        room_id = request.form['room_id']
        description = request.form['description']
        status = request.form['status']
        start_time = datetime.fromisoformat(request.form['start_time'])
        end_time = datetime.fromisoformat(request.form['end_time'])

        user_id = session['user_id']

        # Check if user is organizer
        organizer = Organizer.query.filter_by(user_id=user_id).first()
        if not organizer:
            organizer = Organizer(user_id=user_id)
            db.session.add(organizer)
            db.session.commit()

        # Create meeting
        meeting = Meeting(
            title=title,
            room_id=room_id,
            description=description,
            status=status,
            start_time=start_time,
            end_time=end_time,
            organizer_id=organizer.organizer_id
        )
        db.session.add(meeting)
        db.session.commit()

        create_notification(
        user_id= user_id,
        meeting_id=meeting.meeting_id,
        message=f"Meeting '{meeting.title}' has been created."
    )
        return redirect('/meeting')

    # Fetch meetings hosted by current user
    user_id = session['user_id']
    organizer = Organizer.query.filter_by(user_id=user_id).first()

    hosted_meetings = []
    if organizer:
        hosted_meetings = Meeting.query.filter_by(
            organizer_id=organizer.organizer_id
        ).all()

    # Fetch meetings user has joined as participant
    joined_meetings = (
        db.session.query(Meeting)
        .join(Participant, Participant.meeting_id == Meeting.meeting_id)
        .filter(Participant.user_id == user_id)
        .all()
    )

    return render_template(
        'meeting.html',
        hosted_meetings=hosted_meetings,
        joined_meetings=joined_meetings
    )

@app.route('/join_meeting', methods=['POST'])
@login_required
def join_meeting():
    meeting_id_str = request.form['meeting_id']   # e.g. "00001"
    meeting_id = int(meeting_id_str) 
    user_id = session['user_id']

    meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()
    if not meeting:
        return redirect('/meeting')

    # check if already joined
    existing = Participant.query.filter_by(meeting_id=meeting_id, user_id=user_id).first()
    if existing:
        return redirect('/meeting')

    participant = Participant(meeting_id=meeting_id, user_id=user_id, attendance_status="accepted")
    db.session.add(participant)
    db.session.commit()

    create_notification(
    user_id=user_id,
    meeting_id=meeting_id,
    message=f"You joined the meeting '{meeting.title}'."
    )

    return redirect('/meeting')


@app.route('/update_meeting/<int:meeting_id>', methods=["POST"])
def update_meeting(meeting_id):
    meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()
    old_status = meeting.status
    old_start = meeting.start_time
    old_end = meeting.end_time

    if request.method == "POST":
        title = request.form.get("title")
        room_id = request.form.get("room_id")
        description = request.form.get("description")
        status = request.form.get("status")
        start_time = datetime.fromisoformat(request.form['start_time'])
        end_time = datetime.fromisoformat(request.form['end_time'])

        meeting.title = title
        meeting.room_id = room_id
        meeting.description = description
        meeting.status = status
        meeting.start_time = start_time
        meeting.end_time = end_time
        db.session.add(meeting)       
        db.session.commit()
        if status != old_status:
            # notify host
            create_notification(
                user_id=meeting.organizer.user_id,
                meeting_id=meeting.meeting_id,
                message=f"Meeting '{meeting.title}' status changed from {old_status} to {status}."
            )
            # notify participants
            participants = Participant.query.filter_by(meeting_id=meeting.meeting_id).all()
            for p in participants:
                create_notification(
                    user_id=p.user_id,
                    meeting_id=meeting.meeting_id,
                    message=f"Meeting '{meeting.title}' status changed from {old_status} to {status}."
                )

        # 2️⃣ If timing changed
        if old_start != start_time or old_end != end_time:
            participants = Participant.query.filter_by(meeting_id=meeting.meeting_id).all()
            for p in participants:
                create_notification(
                    user_id=p.user_id,
                    meeting_id=meeting.meeting_id,
                    message=f"Meeting '{meeting.title}' timing updated to {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}."
                )
            # notify host too
            create_notification(
                user_id=meeting.organizer.user_id,
                meeting_id=meeting.meeting_id,
                message=f"Meeting '{meeting.title}' timing updated."
            )
        return redirect('/meeting') 
    return redirect('/meeting')

@app.route('/leave_meeting/<int:meeting_id>', methods=['POST', 'GET'])
@login_required
def leave_meeting(meeting_id):
    user_id = session['user_id']

    # Check if the participant record exists
    participant = Participant.query.filter_by(meeting_id=meeting_id, user_id=user_id).first()
    # Delete participant record
    db.session.delete(participant)
    db.session.commit()
    return redirect('/meeting')

@app.route('/notifications')
@login_required
def view_all_notifications():
    user_id = session['user_id']
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    for n in notifications:
        n.is_read = True
    db.session.commit()
    return render_template('notifications.html', notifications=notifications)


@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    return render_template('login.html')


@app.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    report_data = []
    user_id = session['user_id']
    organizer = Organizer.query.filter_by(user_id=user_id).first()

    meetings = []
    if organizer:
        meetings = Meeting.query.filter_by(organizer_id=organizer.organizer_id).all()

    if request.method == 'POST':
        report_type = request.form.get('report_type')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        selected_statuses = request.form.getlist('status')
        title = request.form.get('title')

        if report_type == 'Participant_Report':
            if title:  # only fetch if meeting selected
                query = (
                    db.session.query(
                    User.name,
                    User.email,
                    Participant.attendance_status,
                    func.to_char(Participant.joined_at, 'YYYY-MM-DD HH12:MI AM').label('joined_at')
                    )
                    .join(Participant, Participant.user_id == User.user_id)
                    .filter(Participant.meeting_id == title)
                   
                )
                report_data = query.all()

        if report_type == 'Room_Utilization_Report':
            if organizer:
                query = (
                    db.session.query(
                        Room.room_name,
                        func.coalesce(func.string_agg(Meeting.title, ', '), 'No meetings held').label('meeting_names'),
                        func.count(Meeting.meeting_id).label('total_meetings'),
                        func.coalesce(
                            func.round(
                                cast(
                                    func.sum(
                                        func.extract('epoch', Meeting.end_time - Meeting.start_time) / 3600.0
                                    ), Numeric
                                ), 1
                            ), 0
                        ).label('total_duration_hours')
                    )
                    .outerjoin(Meeting, Room.room_id == Meeting.room_id)
                    .filter(or_(Meeting.organizer_id == organizer.organizer_id, Meeting.organizer_id == None))
                    .group_by(Room.room_name)
                    .order_by(func.count(Meeting.meeting_id).desc())
                )

                # ✅ Date filters
                if start_date and end_date:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                    end_dt = end_dt.replace(hour=23, minute=59, second=59)
                    query = query.filter(Meeting.start_time.between(start_dt, end_dt))

                elif start_date:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                    query = query.filter(Meeting.start_time >= start_dt)

                elif end_date:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                    end_dt = end_dt.replace(hour=23, minute=59, second=59)
                    query = query.filter(Meeting.start_time <= end_dt)
                report_data = query.all()


        if report_type == 'Meeting_Summary':
            
            if organizer:
                query = (
                    db.session.query(
                        Meeting.meeting_id,
                        Meeting.title,
                        func.date(Meeting.start_time).label('meeting_date'),
                        func.to_char(Meeting.start_time, 'HH12:MI AM').label('meeting_time'),
                        Room.room_name,
                        Meeting.status,
                        func.count(Participant.participant_id).label('participants')
                    )
                    .outerjoin(Participant, Participant.meeting_id == Meeting.meeting_id)
                    .join(Room, Room.room_id == Meeting.room_id)
                    .filter(Meeting.organizer_id == organizer.organizer_id)
                    .group_by(Meeting.meeting_id, Room.room_name)
                )

                if start_date and end_date:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                    end_dt = end_dt.replace(hour=23, minute=59, second=59)
                    query = query.filter(Meeting.start_time.between(start_dt, end_dt))

                elif start_date:  # only start date given
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                    query = query.filter(Meeting.start_time >= start_dt)

                elif end_date:  # only end date given
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                    end_dt = end_dt.replace(hour=23, minute=59, second=59)
                    query = query.filter(Meeting.start_time <= end_dt)

                if selected_statuses:
                    query = query.filter(Meeting.status.in_(selected_statuses))

               

                report_data = query.all()


    return render_template('report.html', report_data=report_data, meetings=meetings, report_type=request.form.get('report_type'))




    

if __name__ == "__main__":
    app.run(debug = True, port = 8000)
