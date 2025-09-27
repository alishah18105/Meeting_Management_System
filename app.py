import os
from flask import Flask, flash, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import redirect, session, url_for, flash


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:ali@localhost:5432/meeting_systemdb"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.urandom(24)
db.init_app(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login first to access this page.", "warning")
            return redirect(url_for('loginPage'))
        return f(*args, **kwargs)
    return decorated_function



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

@app.route('/home',methods=['GET', 'POST'] )
@login_required
def homePage():
    return render_template('menu.html')

@app.route('/meeting', methods = ['GET', 'POST'])
def meeting():
    return render_template('meeting.html')

@app.route('/calendar', methods = ['GET', 'POST'])
def calendar():
    return render_template('calender.html')

@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug = True, port = 8000)