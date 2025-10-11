import os
from flask import Flask, flash, request, render_template, redirect, session
from models import db, User, Notification
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import redirect, session, url_for, flash
from routes.Calendar import calendar_bp 
from sqlalchemy import func, cast, or_
from utilis.auth import login_required
from routes.todo import todo_bp
from routes.dashboard import dashboard_bp
from routes.report import report_bp
from routes.meeting import meeting_bp
from routes.notification import notification_bp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:ali@localhost:5432/meeting_systemdb"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.urandom(24)
app.register_blueprint(calendar_bp)
app.register_blueprint(todo_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(meeting_bp)
app.register_blueprint(report_bp)
app.register_blueprint(notification_bp)


db.init_app(app)
#-----------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------
@app.context_processor
def inject_notifications():
    if 'user_id' in session:
        user_id = session['user_id']
        notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(5).all()
        unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    else:
        notifications, unread_count = [], 0
    return dict(notifications=notifications, unread_count=unread_count)

#-----------------------------------------------------------------------------------------------------
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

#-----------------------------------------------------------------------------------------------------
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
#-----------------------------------------------------------------------------------------------------
@app.route('/home',methods=['GET', 'POST'] )
@login_required
def homePage():
    return render_template('menu.html')

#-----------------------------------------------------------------------------------------------------
@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    return render_template('login.html')


if __name__ == "__main__":
    app.run(debug = True, port = 8000)
