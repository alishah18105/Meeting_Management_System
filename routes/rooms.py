from flask import Blueprint, render_template, request
from models import db, Room, Meeting
from datetime import datetime

rooms_bp = Blueprint('rooms', __name__, template_folder="../templates")

@rooms_bp.route('/rooms', methods=['GET', 'POST'])
def rooms():
    rooms = Room.query.all()
    room_data = []

    if request.method == 'POST':
        date_str = request.form.get('room_date')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')

        if date_str and start_time_str and end_time_str:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_dt = datetime.strptime(f"{date_str} {start_time_str}", "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(f"{date_str} {end_time_str}", "%Y-%m-%d %H:%M")

            for room in rooms:
                overlapping_meetings = Meeting.query.filter(
                    Meeting.room_id == room.room_id,
                    Meeting.start_time < end_dt,
                    Meeting.end_time > start_dt
                ).all()

                is_available = len(overlapping_meetings) == 0

                room_data.append({
                    'room_name': room.room_name,
                    'capacity': room.capacity,
                    'is_available': is_available
                })
        else:
            # Missing input case
            room_data = []
    else:
        now = datetime.now()
        for room in rooms:
            current_meeting = Meeting.query.filter(
                Meeting.room_id == room.room_id,
                Meeting.start_time <= now,
                Meeting.end_time >= now
            ).first()

            is_available = current_meeting is None

            room_data.append({
                'room_name': room.room_name,
                'capacity': room.capacity,
                'is_available': is_available
            })

    return render_template('rooms.html', room_data=room_data)
