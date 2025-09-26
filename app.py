import os
from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:ali@localhost:5432/meeting_systemdb"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.urandom(24)
db.init_app(app)


@app.route('/',methods=['GET', 'POST'] )
def signUpPage():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)


        user_details = User(
            name = name,
            email = email,
            password = hashed_password
        )
        db.session.add(user_details)
        db.session.commit()
    return render_template('signup.html')

@app.route('/login',methods=['GET', 'POST'] )
def loginPage():
    return render_template('login.html')


if __name__ == "__main__":
    app.run(debug = True, port = 8000)