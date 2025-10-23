from flask import Blueprint, jsonify, render_template, request, session, flash, redirect, url_for
from sqlalchemy import Numeric, cast, func, text
from models import Meeting, Participant, Room, db, User
from utilis.auth import login_required
search_bp = Blueprint('search', __name__, template_folder="../templates")

@search_bp.route('/get_user_meetings', methods=['GET', 'POST'])
@login_required 
def get_user_meetings():
    user_id = session.get('user_id')  # assuming you store it in session after login
    if not user_id:
        return jsonify([])

    query = f"""
        SELECT meeting_id, title, description, role
        FROM (
            -- Organizer (Host)
            SELECT 
                m.meeting_id, 
                m.title, 
                m.description, 
                'Host' AS role
            FROM meetings m
            WHERE m.organizer_id = {user_id}
              AND m.status IN ('Ongoing', 'Scheduled')

            UNION

            -- Participant
            SELECT 
                m.meeting_id, 
                m.title, 
                m.description, 
                'Participant' AS role
            FROM meetings m
            JOIN Participants p 
              ON m.meeting_id = p.meeting_id
            WHERE p.user_id = {user_id}
              AND m.status IN ('Ongoing', 'Scheduled')
        ) AS combined;
    """

    result = db.session.execute(text(query)).fetchall()   
    meetings = [
        {"meeting_id": row[0], "title": row[1], "description": row[2], "role": row[3]}
        for row in result
    ]
    return jsonify(meetings)

@search_bp.route('/search', methods=['GET'])
@login_required
def search():
    # Get meeting_id from query parameter (from dropdown)
    meeting_id = request.args.get('meeting_id', type=int)
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    meeting = None
    if meeting_id:
        # Query meeting details with date, time, duration, participants count, room
        query = (
            db.session.query(
                Meeting.meeting_id,
                Meeting.title,
                Meeting.description,
                func.date(Meeting.start_time).label('meeting_date'),
                func.to_char(Meeting.start_time, 'HH12:MI AM').label('meeting_time'),
                Meeting.status,
                func.coalesce(
                    func.round(
                        cast(
                            func.extract('epoch', (Meeting.end_time - Meeting.start_time)) / 3600.0, Numeric
                        ), 1
                    ), 0
                ).label('duration')
            )
            .outerjoin(Participant, Participant.meeting_id == Meeting.meeting_id)
            .filter(Meeting.meeting_id == meeting_id)
            .group_by(Meeting.meeting_id)
        )

        result = query.first()

        if result:
            # Determine role
            role = 'Host' if result.meeting_id and Meeting.query.get(meeting_id).organizer_id == user_id else 'Participant'

            meeting = {
                "meeting_id": result.meeting_id,
                "title": result.title,
                "description": result.description,
                "role": role,
                "meeting_date": result.meeting_date,
                "meeting_time": result.meeting_time,
                "status": result.status,
                "duration": float(result.duration)
            }

    return render_template('search.html', meeting=meeting)