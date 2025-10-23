from models import Form, Participant, db,Meeting,Organizer
from flask import Blueprint,render_template,request,redirect,url_for,flash,session,jsonify
import os
from utilis.auth import login_required
from itsdangerous import URLSafeSerializer

forms_bp=Blueprint("forms",__name__,template_folder="../templates")
SECRET_KEY=os.environ.get("SECRET_KEY","supersecretkey")
serializer=URLSafeSerializer(SECRET_KEY, salt="form-share")

#forms
@forms_bp.route("/templates", methods=["GET", "POST"])
@login_required
def template_gallery():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in first!", "error")
        return redirect(url_for("auth.loginPage"))
    meetings = []
    organizer = Organizer.query.filter_by(user_id=user_id).first()
    if organizer:
        meetings = Meeting.query.filter(Meeting.organizer_id == organizer.organizer_id,
                    Meeting.status != "Cancelled").all()    
    if request.method == "POST":
        filter_type = request.form.get("type")
        meeting_id = request.form.get("meeting")

        if filter_type and meeting_id:
            new_form = Form(
                form_type=filter_type,
                meeting_id=meeting_id,
                user_id=user_id  
            )
            db.session.add(new_form)
            db.session.commit()
            flash("Form generated successfully!", "success")
            return redirect(url_for("forms.template_gallery"))

    participant_meetings = (
        db.session.query(Meeting)
        .join(Participant)
        .filter(Participant.user_id == user_id)
        .all()
    )

    meetings_with_forms = []
    for meeting in participant_meetings:
        form_exists = Form.query.filter_by(meeting_id=meeting.meeting_id).first()
        if form_exists:
            meetings_with_forms.append(meeting)

    # Prepare templates list for rendering
    templates = []
    for m in meetings_with_forms:
        if m.status in ["Scheduled", "Ongoing"]:
            current_type = "before_meeting"
        elif m.status == "Completed":
            current_type = "after_meeting"
        else:
            current_type = "unknown"

        templates.append({
            "id": m.meeting_id,
            "title": m.title,
            "type": current_type
        })

    return render_template("formGallery.html", templates=templates, meetings = meetings)


@forms_bp.route("/forms/<int:meeting_id>/<form_type>")
def open_form(meeting_id, form_type):
    user_id = session.get("user_id")
    meeting = Meeting.query.get_or_404(meeting_id)

    form = Form.query.filter_by(meeting_id=meeting_id, user_id=user_id, form_type=form_type).first()

    if form_type == "before_meeting":
        form_data = {
            "title": f"Pre Meeting Form: {meeting.title}",
            "fields": [
                {"name": "expectations", "label": "What are your expectations from the meeting?", "value": form.expectations if form else ""},
                {"name": "suggestions", "label": "Any suggestion related to meeting?", "value": form.suggestions if form else ""}
            ]
        }
    elif form_type == "after_meeting":
        form_data = {
            "title": f"Post Meeting Form: {meeting.title}",
            "fields": [
                {"name": "feedback", "label": "Your feedback on the meeting?", "value": form.feedback if form else ""},
                {"name": "improvements", "label": "What can be improved for next meeting?", "value": form.improvements if form else ""}
            ]
        }
    else:
        return "Invalid form type", 400

    return render_template("FormFill.html", meeting=meeting, form_type=form_type, form_data=form_data)

#Save Form Data

@forms_bp.route("/form/<int:meeting_id>/<string:form_type>", methods=["GET","POST"])
@login_required
def save_form(meeting_id, form_type):
    user_id = session.get("user_id")
    meeting = Meeting.query.get_or_404(meeting_id)


    try:
        # Check if a form already exists for this user & meeting
        form = Form.query.filter_by(meeting_id=meeting_id, user_id=user_id, form_type=form_type).first()
        if not form:
            form = Form(meeting_id=meeting_id, user_id=user_id, form_type=form_type)
            db.session.add(form)

        if form_type == "before_meeting":
            form.expectations = request.form.get("expectations")
            form.suggestions = request.form.get("suggestions")
            flash(f"Pre Meeting form for '{meeting.title}' saved successfully!", "success")

        elif form_type == "after_meeting":
            form.feedback = request.form.get("feedback")
            form.improvements = request.form.get("improvements")
            flash(f"Post Meeting form for '{meeting.title}' saved successfully!", "success")

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while saving the form: {e}", "error")

    return redirect(url_for("forms.template_gallery"))

#Share Form Link
@forms_bp.route("/form/share/<int:meeting_id>/<string:form_type>",methods=["GET"])
@login_required
def share_form(meeting_id,form_type):
    user_id=session.get("user_id")
    meeting=Meeting.query.get_or_404(meeting_id)

    if meeting.organizer.user_id != user_id:
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
             


