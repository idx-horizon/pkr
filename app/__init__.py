from flask import Flask

from flask_login import LoginManager
from app.config import Config

from flask_sqlalchemy import SQLAlchemy
try:
    from flask_migrate import Migrate
except:
    print('** error: Unable to import flash_migrate')
    
from flask_bootstrap import Bootstrap


app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config.from_object(Config)

db = SQLAlchemy(app)
try:
    migrate = Migrate(app, db)
except:
    print('** error: Unable to migrate db')
#bootstrap = Bootstrap(app)

login = LoginManager(app)
login.login_view = 'login'

#THISDB = app.config['REPOSITORY']
#APPNAME = app.config['APPNAME']
#THISCONFIG = app.config
SELECTEDRUNNER = None

from app import routes, models

