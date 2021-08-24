from datetime import datetime
from app import login, db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func

class LoginLog(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    usernam    = db.Column(db.String(64), index=True)
    time_stamp = db.Column(db.DateTime, nullable=True, server_default=func.now())
    ipaddress  = db.Column(db.String(20))

    def __repr__(self):
        return '{}. {} - {} - {}'.format(self.id, self.ll_datetime, self.ll_username, self.ll_ipaddress)
      
class Country(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    cy_code       = db.Column(db.String(2), index=True, unique=True)
    cy_id         = db.Column(db.Integer, index=True, unique=True)
    cy_name       = db.Column(db.String(20), index=True, unique=True)
    cy_base_url   = db.Column(db.String(50), index=True, unique=True)

    def __repr__(self):
        return '{} ({}) - {}'.format(self.cy_code, self.cy_id, self.cy_name)
    
class Location(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    ln_name       = db.Column(db.String(20), index=True, unique=True)
    ln_lat        = db.Column(db.Float)
    ln_long       = db.Column(db.Float)

    def __repr__(self):
        return '{} ({}, {})'.format(self.ln_name, self.ln_lat, self.ln_long)

class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), index=True, unique=True)
    rid           = db.Column(db.String(10), index=True)
    email         = db.Column(db.String(120), index=True, unique=True)
    agegrade_theshold = db.Column(db.Float)
    password_hash = db.Column(db.String(128))
    home_run      = db.Column(db.String(50))
    home_postcode = db.Column(db.String(50))
    is_admin      = db.Column(db.Boolean)

    def __repr__(self):
        return '{} ({})'.format(self.username, self.rid)
     
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
