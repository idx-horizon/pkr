import os
from flask import Flask, redirect, url_for, session
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from authlib.integrations.flask_client import OAuth

from app.config import Config

try:
    from flask_migrate import Migrate
except:
    print('** error: Unable to import flash_migrate')
    
from flask_bootstrap import Bootstrap

try:
    from flask_googlemaps import GoogleMaps
except: 
    print('** error: Unable to import flask_googlemaps')

app = Flask(__name__, template_folder='../templates', static_folder='../static')

app.config.from_object(Config)

app.secret_key = os.environ['FLASK_SESSION_SECRET_KEY']

try:
    print(app.config['GOOGLEMAPS_KEY'][0:10])
except:
    print('Unable to print GM key')
     
GoogleMaps(app)

oauth = OAuth(app)
pool=os.environ['MY_COG_POOL']
client_id=os.environ['MY_COG_CLIENT']
client_secret=os.environ['MY_COG_SECRET']
authority=f'https://cognito-idp.eu-west-2.amazonaws.com/{pool}'
metadata=f'{authority}/.well-known/openid-configuration'

print('** Metadata_URL:',metadata)

oauth.register(
    name='oidc',
    authority=authority,
    client_id=client_id,
    client_secret=client_secret,
    server_metadata_url=metadata,
    client_kwargs={'scope': 'openid email profile'}
)

db = SQLAlchemy(app)
try:
    migrate = Migrate(app, db)
except:
    print('** error: Unable to migrate db')
    
# bootstrap = Bootstrap(app)

login = LoginManager(app)
login.login_view = 'login'

# THISDB = app.config['REPOSITORY']
# APPNAME = app.config['APPNAME']
# THISCONFIG = app.config
# SELECTEDRUNNER = {'rid': None, 'username': None}

from app import routes, models

