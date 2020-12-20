from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Users(UserMixin, db.Model):
    """ USER TABLE CREATION """

    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key = True)
    username = db.Column(db.String(25), unique = True, nullable = False) #Don't want duplicate user names
    password = db.Column(db.String(), nullable = False)

class Message(db.Model):
    """ MESSAGES TABLE CREATION """

    __tablename__ = 'msg_storage'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25))
    group_name = db.Column(db.String(), nullable = False)
    date_posted = db.Column(db.String(30))
    content = db.Column(db.String())