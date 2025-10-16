from flask import Blueprint, jsonify, render_template, request, redirect, session, url_for
from utilis.auth import login_required
from utilis.create_notifications import create_notification
from datetime import datetime, timedelta
from models import db, Meeting, Room, Organizer, Participant
from utilis.create_notifications import create_notification

meeting_bp = Blueprint('meeting', __name__,template_folder="../templates")

@meeting_bp.route('/meeting', methods=['GET', 'POST'])
@login_required
def meeting():
    rooms = Room.query.all()

    if request.method == 'POST':
        title = request.form['title']
        room_id = request.form['room_id']
        description = request.form['description']
        status = request.form['status']
        start_time = datetime.fromisoformat(request.form['start_time'])
        end_time = datetime.fromisoformat(request.form['end_time'])

        user_id = session['user_id']

        # ✅ Ensure organizer exists
        organizer = Organizer.query.filter_by(user_id=user_id).first()
        if not organizer:
            organizer = Organizer(user_id=user_id)
            db.session.add(organizer)
            db.session.commit()

        # ✅ Create meeting
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

        # ✅ Create notification
        create_notification(
            user_id=user_id,
            meeting_id=meeting.meeting_id,
            message=f"Meeting '{meeting.title}' has been created."
        )

        return redirect(url_for('meeting.meeting'))

    # ✅ Fetch hosted meetings
    user_id = session['user_id']
    organizer = Organizer.query.filter_by(user_id=user_id).first()
    hosted_meetings = []
    if organizer:
        hosted_meetings = Meeting.query.filter_by(
            organizer_id=organizer.organizer_id
        ).all()

    # ✅ Fetch joined meetings
    joined_meetings = (
        db.session.query(Meeting)
        .join(Participant, Participant.meeting_id == Meeting.meeting_id)
        .filter(Participant.user_id == user_id)
        .all()
    )

    return render_template(
        'meeting.html',
        hosted_meetings=hosted_meetings,
        joined_meetings=joined_meetings,
        rooms=rooms
    )

#-----------------------------------------------------------------------------------------------------

@meeting_bp.route('/join_meeting', methods=['POST'])
@login_required
def join_meeting():
    meeting_id_str = request.form['meeting_id']   # e.g. "00001"
    meeting_id = int(meeting_id_str) 
    user_id = session['user_id']
    
    meeting = Meeting.query.filter_by(meeting_id=meeting_id).first()
    if not meeting:
        return redirect(url_for('meeting.meeting'))

    # check if already joined
    existing = Participant.query.filter_by(meeting_id=meeting_id, user_id=user_id).first()
    if existing:
        return redirect(url_for('meeting.meeting'))

    participant = Participant(meeting_id=meeting_id, user_id=user_id, attendance_status="accepted")
    db.session.add(participant)
    db.session.commit()

    create_notification(
    user_id=user_id,
    meeting_id=meeting_id,
    message=f"You joined the meeting '{meeting.title}'."
    )

    return redirect(url_for('meeting.meeting'))

#----------------------------------------------------------------------------------------------------

@meeting_bp.route('/instant_meeting', methods=['POST'])
def instant_meeting():
    rooms = Room.query.all()
    if request.method == 'POST':
        title = request.form['title']
        room_id = request.form['room_id']
        description = request.form['description']
        status = "Ongoing"
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=4)

        user_id = session['user_id']

        # Check if user is organizer
        organizer = Organizer.query.filter_by(user_id=user_id).first()
        if not organizer:
            organizer = Organizer(user_id=user_id)
            db.session.add(organizer)
            db.session.commit()

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

        return jsonify({
            "meeting_id": meeting.meeting_id,
            "title": meeting.title,
            "organizer_id": meeting.organizer_id,
            "user_id": user_id
        })

#----------------------------------------------------------------------------------------------------
@meeting_bp.route('/update_meeting/<int:meeting_id>', methods=["POST"])
def update_meeting(meeting_id):
    rooms = Room.query.all()
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
        return redirect(url_for('meeting.meeting')) 
    return render_template('meeting.html', rooms=rooms)

#----------------------------------------------------------------------------------------------------
@meeting_bp.route('/leave_meeting/<int:meeting_id>', methods=['POST', 'GET'])
@login_required
def leave_meeting(meeting_id):
    user_id = session['user_id']

    # Check if the participant record exists
    participant = Participant.query.filter_by(meeting_id=meeting_id, user_id=user_id).first()
    # Delete participant record
    db.session.delete(participant)
    db.session.commit()
    return redirect(url_for('meeting.meeting'))

#----------------------------------------------------------------------------------------------------
@meeting_bp.route('/delete_meeting/<int:meeting_id>', methods=['POST'])
@login_required
def delete_meeting(meeting_id):
    meeting = Meeting.query.get(meeting_id)
    if meeting:
        db.session.delete(meeting)
        db.session.commit()
        
    return render_template('report.html')



