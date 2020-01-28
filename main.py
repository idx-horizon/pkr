import os
from flask import Flask
from flask import Flask, jsonify, abort, flash, make_response, render_template, redirect, request, url_for, session

from app import app,login
from app.forms import LoginForm
from app.countries import country_dict
from flask_login import UserMixin

import app.newruns as NR

from flask_login import login_user, logout_user, current_user, login_required, UserMixin

class User(UserMixin):
    def __init__(self, id):
        self.id = id
    def get(self):
        return 'ian'

try:
    print('URL request: {}'.format(request))
except:
    pass
    
@login.user_loader
def load_user(id):
    return User.get(id)

@app.errorhandler(404)
def error_404(error):
    try:
        print('URL request: {}'.format(request))
    except:
        pass
    print('** Error: {}'.format(error))
    return redirect('/error/404')

@app.errorhandler(500)
def error_500(error):
    return redirect('/error/500')

@app.route('/error/')
@app.route('/error/<code>')
def error(code=None):
	return render_template('error.html', error_code=code)

@app.route('/')
def index():
	return redirect('/home/')

@app.route('/home/')
def home():
    return render_template('home.html',
                title=get_app_title(),
                file_modified_date=NR.get_last_update())

    
@app.route('/events/', methods=['POST','GET'])
@app.route('/events/<country>/', methods=['POST','GET'])
@app.route('/events/<country>/<filter_str>/', methods=['POST','GET'])
def r_events(country=None, filter_str=None):
    print('r_events {} - method {}'.format( request.url, request.method))
    this_country = country_dict[country or 'uk']	
    this_filter = filter_str or ''
    this_method = 'startswith'
    
    if request.method.upper() == 'POST':
      this_filter  = str(request.form['filter_str']).lower()
      this_method  = str(request.form['filter_method'])
      this_country = str(request.form['country_code'])
      
    print('** Request: [{}] [{}]'.format(request.url, request.method))
    print('** method [{}] country [{}] string [{}]'.format(this_method, this_country, this_filter))
    
    data=NR.getevents_by_filter(this_filter, this_country, this_method)
    return render_template('events.html',
                title=get_app_title() + '[' + str(this_country) + ' | ' + this_filter + ']', 
                filter=this_filter, 
                filter_method=this_method,
                file_modified_date=NR.get_last_update(),
                countries=country_dict,
                country=country,
                data=data)
    
@app.route('/newruns/')
@app.route('/newruns/<limit>')
def newruns(limit=10):
    this_limit =int(limit) or 10
    data = NR.get_last_newruns(this_limit)
    return render_template('newruns.html',
                title=get_app_title(), 
                limit=this_limit, 
                file_modified_date=NR.get_last_update(),
                data=data)

@app.route('/login/', methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    HOME_RUN = None
    form = LoginForm()
    if form.validate_on_submit():
        print('Validating: [{}] [{}]'.format(form.username.data, form.password.data))
        user = User(form.username.data)
#        user = User.query.filter_by(username=form.username.data).first()
#        if user is None or not user.check_password(form.password.data):
        if user.id != 'ian' or form.password.data != 'p':
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)

    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


def get_app_title():
    return os.environ['APP_TITLE'] 

def runapp(host='localhost', port=5000, debug=True):
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    port=5000
    debug=True
    host='localhost'
    runapp(host=host, port=port, debug=debug)
