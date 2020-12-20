import os
import time

from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, current_user, logout_user

from flask_socketio import SocketIO, join_room, leave_room, send
from flask_form import *
from models import *
from collections import OrderedDict

#Configuring Flask App
app = Flask(__name__)
#app.secret_key=os.environ.get('SECRET')
#app.config['WTF_CSRF_SECRET_KEY'] = b"f\xfa\x8b{X\x8b\x9eM\x83l\x19\xad\x84\x08\xaa"
app.config['SECRET_KEY'] = 'E2C6B2E19E4A7777'

#Configuring Database
app.config['SQLALCHEMY_DATABASE_URI']='postgres://xeybkmoxcrcwrm:f535f8815f0eb688aa3988a9376bccbabb413c94d275ab3b3ff152535244a9fe@ec2-35-172-246-19.compute-1.amazonaws.com:5432/d4018l2sjbnlb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Confuguring Flask Session
login = LoginManager(app)
login.init_app(app)

@login.user_loader
def load_user(id):
    return Users.query.get(int(id))

#Initialize Flask-SocketIO
socketio = SocketIO(app)
# Predefined rooms for chat
ROOMS = ["lounge", "news", "sports", "coding"]


@app.route('/', methods = ['GET','POST'])
def index():
    reg_form = RegistrationForm()
    
    #Update Database if Validation is successful
    if reg_form.validate_on_submit():
        user = reg_form.username.data
        password = reg_form.password.data
        
        #Password Hashing 
        hashed_password = pbkdf2_sha256.hash(password)

        #Adding the new user into Database
        new_user = Users(username = user, password = hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registered successfully. Please login.', 'success')

        return redirect(url_for('login'))
    
    return render_template("index.html", form = reg_form)

@app.route('/login', methods = ['GET','POST'])
def login():
    login_form = LoginForm()
    
    if login_form.validate_on_submit():
        user_obj = Users.query.filter_by(username = login_form.username.data).first()
        login_user(user_obj)
        return redirect(url_for('chat'))

    return render_template('login.html', form = login_form)

@app.route('/chat', methods = ['GET', 'POST'])
def chat():
    if not current_user.is_authenticated:
        flash('Please login.', 'danger')
        return redirect(url_for('login'))
    
    return render_template("chat.html", username=current_user.username, rooms=ROOMS)


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

@app.route('/logout', methods = ['GET'])
def logout():
    logout_user()
    flash('You have logged out successfully', 'success')
    return redirect(url_for('login'))


@socketio.on('incoming-msg')
def on_message(data):
    """Broadcast messages"""

    msg = data["msg"]
    username = data["username"]
    room = data["room"]
    # Set timestamp
    time_stamp = time.strftime('%b-%d %I:%M%p', time.localtime())
    """Save messages"""
    new_msg = Message(username = username, group_name = room, date_posted = time_stamp, content = msg)
    db.session.add(new_msg)
    db.session.commit()

    send({"username": username, "msg": msg, "time_stamp": time_stamp}, room=room)


@socketio.on('join')
def on_join(data):
    """User joins a room"""

    user = data["username"]
    room = data["room"]
    join_room(room)

    # Broadcast that new user has joined
    send({"msg": user + " has joined the " + room + " room."}, room=room)
    
    messages = Message.query.filter_by(group_name=room).all()
    for msgs in messages:
        user = msgs.username
        user = [user]
        msg = msgs.content
        msg = [msg]
        time_stamp = msgs.date_posted
        time_stamp = [time_stamp]
        send({"username": user, "msg": msg, "time_stamp": time_stamp}, room=room)

@socketio.on('leave')
def on_leave(data):
    """User leaves a room"""

    username = data['username']
    room = data['room']
    leave_room(room)
    send({"msg": username + " has left the room"}, room=room)

if __name__ == "__main__":
    app.run()
