from sqlalchemy import cast
from operator import or_
from flask import Blueprint, render_template, request, redirect, session
from datetime import datetime, timedelta
from sqlalchemy import Numeric, func
from models import Participant, User, db, Meeting, Room, Organizer
from utilis.auth import login_required
from utilis.create_notifications import create_notification
report_bp = Blueprint('report', __name__,template_folder="../templates")

@report_bp.route('/report', methods=['GET', 'POST'])
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



