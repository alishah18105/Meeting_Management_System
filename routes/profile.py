from flask import Blueprint, render_template, session,flash,redirect,url_for,request
from utilis.auth import login_required
from models import User,db
from datetime import datetime 

profile_bp=Blueprint("profile",__name__,template_folder="../templates")
@profile_bp.route("/profile",methods=["GET","POST"])
@login_required
def profile():
    user_id=session.get("user_id")
    user=User.query.get(user_id)
    plain_pw=session.get('plain_password')

    if request.method == "POST":
        user.role=request.form.get("role") or user.role
        user.department=request.form.get("department") or user.department
        user.phone=request.form.get("phone") or user.phone
        user.dob=request.form.get("dob") or user.dob
        user.address=request.form.get("address") or user.address
        db.session.commit()
        flash("Profile updated successfully","success")
        return redirect(url_for("profile.profile"))

    return render_template(
    "profile.html",
    username=user.name,
    email=user.email,
    plain_password=plain_pw,
    role=user.role,
    department=user.department,
    phone=user.phone,
    dob=user.dob,
    address=user.address,
    login_time=session.get("login_time")
  )