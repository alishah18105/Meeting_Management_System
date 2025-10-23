from models import db,Meeting,Organizer
from flask import Blueprint,render_template,request,redirect,url_for,flash,session,jsonify
import os
from utilis.auth import login_required
from itsdangerous import URLSafeSerializer

forms_bp=Blueprint("forms",__name__,template_folder="../templates")
SECRET_KEY=os.environ.get("SECRET_KEY","supersecretkey")
serializer=URLSafeSerializer(SECRET_KEY, salt="form-share")

#forms
@forms_bp.route("/templates",methods=["GET"])
@login_required
def template_gallery():
    user_id=session.get("user_id")
    if not user_id:
        flash("Please log in first!","error")
        return redirect(url_for("auth.loginPage"))

    filter_type=request.args.get("type","all")
    meetings_query = (
        Meeting.query.join(Organizer)
        .filter(Organizer.user_id == user_id)
        .filter(Meeting.status != "Cancelled")  
    )  
    if filter_type=="before_meeting":
        meetings_query=meetings_query.filter(Meeting.status.in_(["Scheduled","Ongoing"]))
    elif filter_type=="after_meeting":
        meetings_query=meetings_query.filter(Meeting.status=="Completed")    
    meetings=meetings_query.all()

    templates=[]
    for m in meetings:
        if m.status in ["Scheduled","Ongoing"]:
            current_type="before_meeting"
        elif m.status=="Completed":
            current_type="after_meeting"
        else:
            current_type="unknown"

        templates.append({
            "id":m.meeting_id,
            "title":m.title,
            "type":current_type
        })       
    return render_template("formGallery.html",templates=templates,current_type=filter_type)         

#open form
@forms_bp.route("/form/<int:meeting_id>/<string:form_type>",methods=["GET"])
@login_required
def open_form(meeting_id,form_type):
    user_id=session.get("user_id")
    meeting=Meeting.query.get_or_404(meeting_id)

    if meeting.organizer.user_id!=user_id:
        flash("You are not authorized to access this meeting form","error")
        return redirect(url_for("forms.template_gallery"))
    if form_type=="before_meeting":
        form_data={
            "title":f"Pre Meeting Form: {meeting.title}",
            "fields":[
                {"name":"before_expectation","label":"What are your expectations?","value":meeting.before_expectation or ""},
                {"name":"before_topics","label":"Key topics to discuss?","value":meeting.before_topics or ""}
            ]
        }
    elif form_type=="after_meeting":
        form_data={
            "title":f"Post Meeting Form: {meeting.title}",
            "fields":[
                {"name":"after_feedback","label":"Your feedback on the meeting?","value":meeting.after_feedback or ""},
                {"name":"after_outcome","label":"What was the key outcome/action?","value":meeting.after_outcome or ""}
            ]
        }         
    else:
        flash("Invalid form type","error")
        return redirect(url_for("forms.template_gallery"))

    return render_template("FormFill.html",meeting=meeting,form_type=form_type,form_data=form_data)    

#Save Form Data
@forms_bp.route("/form/<int:meeting_id>/<string:form_type>",methods=["POST"])
@login_required
def save_form(meeting_id,form_type):
    user_id=session.get("user_id")
    meeting=Meeting.query.get_or_404(meeting_id)

    if meeting.organizer.user_id!=user_id:
        flash("You are not authorized to access this meeting form","error")
        return redirect(url_for("forms.template_gallery"))    
    try:
        if form_type=="before_meeting":
            meeting.before_expectation=request.form.get("before_expectation")    
            meeting.before_topics=request.form.get("before_topics")
            if meeting.status=="Scheduled":
                meeting.status="Ongoing"
            flash(f"Pre-Meeting form for'{meeting.title}' saved successfully!","success")

        elif form_type=="after_meeting":
            meeting.after_feedback=request.form.get("after_feedback")    
            meeting.after_outcome=request.form.get("after_outcome")
            meeting.status="Completed"
            flash(f"Post-Meeting form for'{meeting.title}' saved successfully!","success")    

        db.session.commit()
    
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while saving the form: {e}","error")
    
    return redirect(url_for("forms.template_gallery"))     

#Share Form Link
@forms_bp.route("/form/share/<int:meeting_id>/<string:form_type>",methods=["GET"])
@login_required
def share_form(meeting_id,form_type):
    user_id=session.get("user_id")
    meeting=Meeting.query.get_or_404(meeting_id)

    if meeting.organizer.user_id != user_id:
        flash("You are not authorized to access this meeting form","error")
        return redirect(url_for("forms.template_gallery"))  

    token=serializer.dumps({"meeting_id":meeting_id,"form_type":form_type})
    share_url=url_for("forms.shared_form",token=token,_external=True)    
    return jsonify({"share_url":share_url})

#Open Shared Form 
@forms_bp.route("/form/shared/<string:token>",methods=["GET"])
def shared_form(token):
    try:
        data=serializer.loads(token)
        meeting_id=data["meeting_id"]
        form_type=data["form_type"]
    except Exception:
        flash("Invalid or expired share link","error")
        return redirect(url_for("forms.template_gallery"))
    return open_form(meeting_id,form_type)                
             


