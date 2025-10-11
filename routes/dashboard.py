from flask import Blueprint,render_template,session,flash,redirect,url_for
from datetime import datetime,timedelta
from functools import wraps
from models import db,Todo,Meeting,Organizer,Participant,Notification,Event,Room
from sqlalchemy import func 
from utilis.auth import login_required
dashboard_bp=Blueprint("dashboard",__name__,template_folder="../templates")

def get_dashboard():
    user_id=session.get("user_id")
    if not user_id:
        flash("Please log in first","warning")
        return {}
        

        #Meeting card
    organizer=Organizer.query.filter_by(user_id=user_id).first()
    hosted_meetings=Meeting.query.filter_by(organizer_id=organizer.organizer_id).all() if organizer else []
    joined_meetings=(
            db.session.query(Meeting)
            .join(Participant,Participant.meeting_id==Meeting.meeting_id)
            .filter(Participant.user_id==user_id)
            .all()
    )
    now=datetime.now()
    all_meetings={m.meeting_id:m for m in hosted_meetings+joined_meetings}.values()
    scheduled_meetings=sum(1 for m in all_meetings if m.status =="Scheduled")
    cancelled_meetings=sum(1 for m in all_meetings if m.status =="Canceled")
    total_meetings=len(all_meetings)
 
        #Calendar Card
    today=datetime.now().date()
    first_day_this_month=today.replace(day=1)
    last_day_last_month=first_day_this_month-timedelta(days=1)
    first_day_last_month=last_day_last_month.replace(day=1)

    last_month_meetings=sum(
            1 for m in all_meetings
            if m.start_time and first_day_last_month<=m.start_time.date()<=last_day_last_month

    )
    upcoming_meetings=sum(
            1 for m in all_meetings
            if m.start_time and m.start_time.date()>=today and m.status.lower() in ["scheduled"]
    )
    upcoming_user_events=Event.query.filter(
            Event.created_by==user_id,
            Event.event_date>=today
    ).count()
    upcoming_events=upcoming_meetings+upcoming_user_events

    reminders=Notification.query.filter_by(user_id=user_id,is_read=False).count()

    start_of_week=today-timedelta(days=today.weekday())
    end_of_week=start_of_week+timedelta(days=6)
    calendar_events_this_week=Event.query.filter(
            Event.created_by==user_id,
            Event.event_date>=start_of_week,
            Event.event_date<=end_of_week
    ).all()

    meetings_this_week=[
            m for m in all_meetings
            if m.start_time and start_of_week <=m.start_time.date()<=end_of_week and m.status.lower() in["scheduled"]
    ]
    events_this_week=calendar_events_this_week+meetings_this_week
    future_meetings=[m for m in all_meetings if m.start_time and m.start_time>= now and m.status.lower() in ["scheduled"]]
    next_meeting=min(future_meetings,key=lambda m: m.start_time) if future_meetings else None

        #Room Card
       
    booked_rooms_ids=(
            db.session.query(Meeting.room_id)
            .filter(Meeting.end_time>=now)
            .distinct()
            .all()
    )
    booked_rooms_ids=[r[0] for r in booked_rooms_ids]
    booked_rooms=len(booked_rooms_ids)
    total_rooms=Room.query.count()
    utilization=(booked_rooms/total_rooms *100) if total_rooms>0 else 0
        
    most_used_rooms=(
            db.session.query(Room.room_name,func.count(Meeting.meeting_id))
            .join(Meeting,Room.room_id==Meeting.room_id)
            .group_by(Room.room_name)
            .order_by(func.count(Meeting.meeting_id).desc())
            .limit(3)
            .all()
    )
    todos=Todo.query.filter_by(created_by=user_id).all()

    return{
            "scheduled_meetings":scheduled_meetings,
            "cancelled_meetings":cancelled_meetings,
            "total_meetings":total_meetings,
            "upcoming_events":upcoming_events,
            "reminders":reminders,
            "todos":todos,
            "last_month_meetings":last_month_meetings,
            "total_rooms":total_rooms,
            "booked_rooms":booked_rooms,
            "utilization":utilization,
            "most_used_rooms":most_used_rooms,
            "events_this_week":events_this_week,
            "next_meeting":next_meeting
    }
@dashboard_bp.route("/home")  
@login_required
def home():
    data=get_dashboard()
    return render_template("menu.html",**data)
       
