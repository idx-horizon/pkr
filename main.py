import os
from flask import Flask
from flask import Flask, jsonify, abort, flash, make_response, render_template, redirect, request, url_for, session
from operator import attrgetter

from app import app,login,db
from app.forms import LoginForm
from app.countries import country_dict
from app.track import Tracker
from app.country_list import centres

import app.newruns as NR
import app.utils as utils
import app.summaries as summaries

from flask_login import login_user, logout_user, current_user, login_required, UserMixin

from app.models import User
app_TRACKER = Tracker()



#class User(UserMixin):
#    def __init__(self, id):
#        self.id = id
#    def get(self):
#       return 'ian' #self.id #current_user #'ian'

try:
    print('URL request: {}'.format(request))
except:
    pass

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

    
#@login.user_loader
#def load_user(id):
#    return User.get(id)

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

        
@app.route('/api/v1/meta', methods=['POST','GET'])
def apilog():
    global app_TRACKER
    
    app_TRACKER.update(request)

    payload = app_TRACKER.meta

    if request.method.upper() == 'POST':
        return jsonify(payload)
    else:
        return render_template('apilog.html', payload=payload)


@app.route('/home/')
def home():
    return render_template('home.html',
                title=get_app_title(),
                file_modified_date=NR.get_last_update())

    
@app.route('/events/', methods=['POST','GET'])
@app.route('/events/<country>/', methods=['POST','GET'])
@app.route('/events/<country>/<filter_str>/', methods=['POST','GET'])
@app.route('/events/<country>/<filter_str>/<centre_on_code>/', methods=['POST','GET'])
def r_events(country=None, filter_str=None, centre_on_code=None):
    print('r_events {} - method {} - centre {}'.format( 
            request.url, 
            request.method,
            centre_on_code))
    this_country = country or 'uk'	
    this_filter = filter_str or ''
    this_method = 'startswith'
    if not current_user.is_anonymous:
        this_centre_on = centre_on_code or current_user.home_run
    else:
        this_centre_on = centre_on_code or 'bushy'
    
    if request.method.upper() == 'POST':
      this_filter  = str(request.form['filter_str']).lower()
      this_method  = str(request.form['filter_method'])
      this_country = str(request.form['country_code'])
      this_centre_on = str(request.form['centre_on_code'])
    
    data=NR.getevents_by_filter(this_filter, country_dict[this_country], this_method, this_centre_on)
    data = sorted(data, key=attrgetter('distance'))

    if not current_user.is_anonymous:
        base_runner = current_user.rid 
        rid = utils.Runner(str(base_runner).lower())
        rid.get_runs(this_filter, False)

        for d in data:
            if d.evshortname in [x['Event'] for x in rid.runs]:
                d.set_hasrun('Yes')
        
    return render_template('events.html',
                title=get_app_title() + '[' + str(this_country) + ' | ' + this_filter + ']', 
                filter=this_filter, 
                filter_method=this_method,
                file_modified_date=NR.get_last_update(),
                countries=country_dict,
                country=this_country,
                centres=centres.keys(),
                centre_on=this_centre_on,
                data=data)

@app.route('/stats', methods=['POST','GET'])
def runner_stats():
    if not current_user.is_anonymous:
        rid = utils.Runner(str(current_user.rid).lower())
    else:
        return redirect(url_for('login'))

    rid.get_runs(None,False)
    rid.updated_dt = rid.updated_dt.strftime('%d-%b-%Y %H:%M')

    return render_template('stats.html',
                title=get_app_title(), 
                file_modified_date=NR.get_last_update(),
                data=rid)

@app.route('/runs', methods=['POST','GET'])
@app.route('/runs/', methods=['POST','GET'])
@app.route('/runs/<filter_str>/', methods=['POST','GET'])
def runner_runs(filter_str=None):
    if not current_user.is_anonymous:
        rid = utils.Runner(str(current_user.rid).lower())
    else:
        return redirect(url_for('login'))

    this_filter = filter_str or ''

    if request.method.upper() == 'POST':
      this_filter  = str(request.form['filter_str']).lower()

    rid.get_runs(this_filter, False)
    rid.updated_dt = rid.updated_dt.strftime('%d-%b-%Y %H:%M')

    return render_template('runs.html',
                title=get_app_title(), 
                file_modified_date=NR.get_last_update(),
                data=rid,
                threshold=rid.threshold)


        
@app.route('/newevents/', methods=['POST','GET'])
@app.route('/newevents/<country>/', methods=['POST','GET'])
@app.route('/newevents/<country>/<limit>/', methods=['POST','GET'])
def r_newevents(limit=10, country=None):
    this_limit =int(limit) or 10
    this_country = country or 'uk'	

    
    if request.method.upper() == 'POST':
      this_limit = str(request.form['limit'])
      this_country = str(request.form['country_code'])
    
    data = NR.get_last_newruns(int(this_limit), country_dict[this_country])
    
#    data = sorted(data, key=attrgetter('distance'))
    data = sorted(data, reverse=True, key=attrgetter('evid'))
    return render_template('newevents.html',
                title=get_app_title(), 
                limit=this_limit, 
                countries=country_dict,
                country=this_country,
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
        #user = User(form.username.data)
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)

    return render_template('login.html', title='Login', form=form)

@app.route('/summaries/year')
@login_required
def r_year_summary():
    #if not current_user.is_anonymous:
    rid = utils.Runner(str(current_user.rid).lower())
    #else:
    #    return redirect(url_for('login'))
        
    rid.get_runs(None, False)

    data = summaries.year_summary(rid.runs)
    return render_template('summary_year.html', 
                            title='Year Summary', 
                            data=data)

@app.route('/summaries/event')
@login_required
def r_event_summary():
    #if not current_user.is_anonymous:
    rid = utils.Runner(str(current_user.rid).lower())
    #else:
    #    return redirect(url_for('login'))
        
    rid.get_runs(None, False)

    data = summaries.event_summary(rid.runs)
    return render_template('summary_event.html', 
                            title='Event Summary', 
                            data=data)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/user')
def user_details():
    return render_template('user.html')


def get_app_title():
    return os.environ['APP_TITLE'] 

def runapp(host='localhost', port=5000, debug=True):
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    port=5000
    debug=True
    host='localhost'
    runapp(host=host, port=port, debug=debug)
