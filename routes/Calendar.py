from models import db,Event,Meeting,Participant,Organizer
from flask import Blueprint,render_template,request,redirect,url_for,flash,session
import calendar
from datetime import datetime
from functools import wraps

calendar_bp=Blueprint("calendar",__name__,template_folder="../templates")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login first to access this page.", "warning")
            return redirect(url_for('loginPage'))
        return f(*args, **kwargs)
    return decorated_function


#Calendar View
@calendar_bp.route("/calendar")
@login_required
def index():
    today=datetime.today()
    month=int(request.args.get("month",today.month))
    year=int(request.args.get("year",today.year))
    edit_id=request.args.get("edit_id",type=int)
    user_id=session.get("user_id")

    month_name=calendar.month_name[month]
    cal=calendar.Calendar()
    days=list(cal.itermonthdays(year,month))

    events=Event.query.filter_by(created_by=user_id).all()
    
    hosted_meetings=[]
    joined_meetings=[]
    
    organizer=Organizer.query.filter_by(user_id=user_id).first()
    if organizer:
        hosted_meetings=Meeting.query.filter_by(
            organizer_id=organizer.organizer_id,
            status="Scheduled"
        ).all()
    

    joined_meetings=(
        db.session.query(Meeting)
        .join(Participant,Participant.meeting_id==Meeting.meeting_id)
        .filter(
            Participant.user_id==user_id,
            Meeting.status=="Scheduled"
        ).all()
    )    

    scheduled_meetings=list(
        {m.meeting_id: m for m in hosted_meetings + joined_meetings}.values())


    all_events=[]
    for e in events:
        all_events.append({
            "id":e.event_id,
            "title":e.title,
            "date":e.event_date,
            "type":"event"
        })
    for m in scheduled_meetings:
        all_events.append({
            "id":m.meeting_id,
            "title":f"Meeting: {m.title}",
            "date":m.start_time.date(),
            "type":"meeting"
        })    

    events_by_day={}
    for e in all_events:
        if e["date"].month==month and e["date"].year==year:
            day=e["date"].day
            events_by_day.setdefault(day,[]).append(e)

    prev_month=month-1 or 12
    prev_year=year-1 if month==1 else year
    next_month=month+1 if month<12 else 1
    next_year=year +1 if month==12 else year

    return render_template(
        "Calendar.html",
        month=month,
        year=year,
        month_name=month_name,
        days=days,
        events_by_day=events_by_day,
        prev_month=prev_month,
        prev_year=prev_year,
        next_month=next_month,
        next_year=next_year,
        allEvents=all_events,
        edit_id=edit_id
        )         
#Add Event
@calendar_bp.route("/calendar/add",methods=["POST"])
@login_required
def add_event():
    title=request.form.get("title")
    date=request.form.get("date")
    user_id=session.get("user_id")

    if not user_id:
        flash("You must be logged in!","warning")
       
    
    if not title or not date:
        flash("Title and date are required!","warning")
        return redirect(url_for("calendar.index"))

    new_event=Event(title=title,event_date=date,created_by=user_id)
    db.session.add(new_event)
    db.session.commit()
    flash("Event added successfully","success")
    return redirect(url_for("calendar.index"))

#Open Edit Event Form
@calendar_bp.route("/calendar/edit/<int:event_id>",methods=["GET"])
@login_required
def edit_event(event_id):
        event=Event.query.get_or_404(event_id)
        return render_template("edit_event.html",event=event)

#Update Event    
@calendar_bp.route("/calendar/update/<int:event_id>",methods=["POST"])
@login_required
def update_event(event_id):
        event=Event.query.get_or_404(event_id)
        event.title=request.form.get("title")
        event.event_date=request.form.get("date")
        db.session.commit()
        flash("Event updated successfully","success")
        return redirect(url_for("calendar.index"))

#Delete Event
@calendar_bp.route("/calendar/delete/<int:event_id>",methods=["POST"])
@login_required
def delete_event(event_id):
      event=Event.query.get_or_404(event_id)
      db.session.delete(event)
      db.session.commit()
      flash("Event deleted successfully","success")
      return redirect(url_for("calendar.index"))

#Search Event
@calendar_bp.route("/calendar/search")
def search():
     q=request.args.get("q","").strip()
     user_id=session.get("user_id")
     today=datetime.today()
     month=today.month
     year=today.year

     if q:
          events=Event.query.filter(
              Event.title.ilike(f"%{q}%"),Event.created_by==user_id).all()
          meetings=(
               Meeting.query.filter(
              Meeting.title.ilike(f"%{q}%"),Meeting.status=="Scheduled")
              .join(Organizer,Organizer.organizer_id==Meeting.organizer_id)
              .filter(Organizer.user_id==user_id)
              .all()
          )
     else:
          events=Event.query.filter_by(created_by=user_id).all()
          meetings=(
               Meeting.query.join(Organizer) 
               .filter(Organizer.user_id==user_id, Meeting.status=="Scheduled")
               .all()
          )

     all_events=[]
     for e in events:
        all_events.append({
            "id":e.event_id,
            "title":e.title,
            "date":e.event_date,
            "type":"event"
        })
     for m in meetings:
        all_events.append({
            "id":m.meeting_id,
            "title":f"Meeting: {m.title}",
            "date":m.start_time.date(),
            "type":"meeting"
        })    

     events_by_day={}
     for e in all_events:
        if e["date"].month==month and e["date"].year==year:
            day=e["date"].day
            events_by_day.setdefault(day,[]).append(e)
     
     month_name=calendar.month_name[month]
     cal=calendar.Calendar()
     days=list(cal.itermonthdays(year,month))
     prev_month=month-1 or 12
     prev_year=year-1 if month==1 else year
     next_month=month+1 if month<12 else 1
     next_year=year +1 if month==12 else year

     return render_template(
        "Calendar.html",
        month=month,
        year=year,
        month_name=month_name,
        days=days,
        events_by_day=events_by_day,
        prev_month=prev_month,
        prev_year=prev_year,
        next_month=next_month,
        next_year=next_year,
        allEvents=all_events,
       
        )         




     