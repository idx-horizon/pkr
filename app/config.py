import os
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Gardens grows Sox and Candles'
    USER_AGENT = 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36'
    APPNAME = 'PKR' #os.environ.get('RR_NAME') or 'Unknown'

 
    REPOSITORY = APPNAME + '_static.db'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, REPOSITORY)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

