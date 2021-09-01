import os
from flask import Flask, jsonify, abort, flash, make_response, render_template, redirect, request, url_for, session
from flask_login import login_user, logout_user, current_user, login_required, UserMixin

from operator import attrgetter
from werkzeug.urls import url_parse

from app import app,login,db

from app.track import Tracker
from app.models import User, Country, Location, LoginLog, Friend
from app.forms import LoginForm
from app.resources import country_dict, centres
import app.newruns as NR
import app.utils as utils
import app.summaries as summaries
import datetime

import pygal

app_TRACKER = Tracker()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

@app.context_processor
def inject_context():
    return dict(selected_runner=session['SELECTEDRUNNER'],
                friends=session['FRIENDS'],
                title = os.environ['APP_TITLE'])
    
@app.template_filter()
def format_datetime(value, 
                    format_src='%d/%m/%Y', 
                    format_out='%d-%b-%Y'):
    x = datetime.datetime.strptime(value, format_src)
    return x.strftime(format_out)
    
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

@app.route('/graph')
def r_graph():
    SELECTEDRUNNER = session['SELECTEDRUNNER']
    rid = utils.Runner(SELECTEDRUNNER['rid'] or current_user.rid)

    rid.get_runs(None,False)
    mx_runs = 100
    
    try:
       graph = pygal.Line()
#       graph.title = 'Languages over time.'
#       graph.x_labels = ['2012','2013','2014','2015','2016']
#       graph.add('Python',  [15, 31, 89, 200, 356])
#       graph.add('Java',    [15, 45, 76, 80,  91])
#       graph.add('C++',     [5,  51, 54, 102, 150])
       graph.title = 'Last {} runs'.format(mx_runs)
       subset = rid.runs[:mx_runs]
       
#       graph.x_labels = [x['Run Date'] for x in subset]
       graph.add(SELECTEDRUNNER['username'].title(), 
                [float(x['AgeGrade'].replace('%','')) for x in subset])
                
       for f in Friend.get(SELECTEDRUNNER['username']):
           print('Add to graph', f) 
 #          graph.add(f.f_username].title(), 
 #               [float(x['AgeGrade'].replace('%','')) for x in subset])
                
       graph.range = [20, 80]
       graph_data = graph.render_data_uri()
       return render_template("graph.html", 
                                graph_title = graph.title,
                                graph_data = graph_data)
    except Exception as e:
       return(str(e))
      
@app.route('/home/')
def home():
    return render_template('home.html',
                file_modified_date=NR.get_last_update())

    
@app.route('/events/', methods=['POST','GET'])
@app.route('/events/<country>/', methods=['POST','GET'])
@app.route('/events/<country>/<filter_str>/', methods=['POST','GET'])
@app.route('/events/<country>/<filter_str>/<centre_on_code>/', methods=['POST','GET'])
def r_events(country=None, filter_str=None, centre_on_code=None):
    SELECTEDRUNNER = session['SELECTEDRUNNER']
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

    print('** has_run args', request.args.get('filter','not set'))
    print('** all args', request.args)
    
    data=NR.getevents_by_filter(this_filter, country_dict[this_country]['id'], this_method, this_centre_on)
    data = sorted(data, key=attrgetter('distance'))

    if not current_user.is_anonymous:
        base_runner = SELECTEDRUNNER['rid'] or current_user.rid
        rid = utils.Runner(str(base_runner).lower())
        rid.get_runs(this_filter, False)

        for d in data:
            if d.evshortname in [x['Event'] for x in rid.runs]:
                d.set_hasrun('Yes')
                try:
                    occ = max([x['occurrences'] for x in rid.runs if x['Event']==d.evshortname])
                    d.set_occurrences(occ)
                except:
                    pass
                    
    return render_template('events.html',
                filter=this_filter, 
                filter_method=this_method,
                file_modified_date=NR.get_last_update(),
                countries=country_dict,
                country=this_country,
                centres=centres.keys(),
                centre_on=this_centre_on,
                data=data)

@app.route('/stats', methods=['POST','GET'])
@login_required
def runner_stats():
    SELECTEDRUNNER = session['SELECTEDRUNNER']
    rid = utils.Runner(SELECTEDRUNNER['rid'] or current_user.rid)

    rid.get_runs(None,False)
    rid.updated_dt = rid.updated_dt.strftime('%d-%b-%Y %H:%M')

    return render_template('stats.html',
                file_modified_date=NR.get_last_update(),
                data=rid)

@app.route('/runs', methods=['POST','GET'])
@app.route('/runs/', methods=['POST','GET'])
@app.route('/runs/<filter_str>/', methods=['POST','GET'])
@login_required
def runner_runs(filter_str=None):
    SELECTEDRUNNER = session['SELECTEDRUNNER']
    rid = utils.Runner(SELECTEDRUNNER['rid'] or current_user.rid)

    this_filter = filter_str or ''

    if request.method.upper() == 'POST':
      this_filter  = str(request.form['filter_str']).lower()

    rid.get_runs(this_filter, False)
    rid.updated_dt = rid.updated_dt.strftime('%d-%b-%Y %H:%M')

    return render_template('runs.html',
        file_modified_date=NR.get_last_update(),
        data=rid,
        filter=this_filter,
        threshold='{:05.2f}'.format(SELECTEDRUNNER.threshold))

@app.route('/loginlog/', methods=['POST','GET'])
def r_loginlog():
    data = LoginLog.get_log()
    return render_template('loginlog.html',
                data=data)

        
@app.route('/newevents/', methods=['POST','GET'])
@app.route('/newevents/<country>/', methods=['POST','GET'])
@app.route('/newevents/<country>/<limit>/', methods=['POST','GET'])
def r_newevents(limit=10, country=None):
    this_limit =int(limit) or 10
    this_country = country or 'uk'	

    
    if request.method.upper() == 'POST':
      this_limit = str(request.form['limit'])
      this_country = str(request.form['country_code'])
    
    data = NR.get_last_newruns(int(this_limit), country_dict[this_country]['id'])
    
#    data = sorted(data, key=attrgetter('distance'))
    data = sorted(data, reverse=True, key=attrgetter('evid'))
    return render_template('newevents.html',
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
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            LoginLog.add('***' + form.username.data.lower(), request.headers['X-Real-IP'])
            
            return redirect(url_for('login'))
            
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('runner_runs')
            
        LoginLog.add(form.username.data.lower(), request.headers['X-Real-IP'])
        session['SELECTEDRUNNER'] = {
            'username': user.username, 
            'rid': user.rid, 
            'threshold': user.agegrade_theshold, 
            'icon': rid.icon}
        session['FRIENDS'] = Friend.get(user.username)
        return redirect(next_page)

    return render_template('login.html', title='Login', form=form)

@app.route('/summaries/year')
@login_required
def r_year_summary():
    SELECTEDRUNNER = session['SELECTEDRUNNER']
    rid = utils.Runner(SELECTEDRUNNER['rid'] or current_user.rid)
    rid.get_runs(None, False)

    data = summaries.year_summary(rid.runs)
    return render_template('summary_year.html', 
                            data=data)

@app.route('/summaries/event')
@login_required
def r_event_summary():
    SELECTEDRUNNER = session['SELECTEDRUNNER']
    rid = utils.Runner(SELECTEDRUNNER['rid'] or current_user.rid)
        
    rid.get_runs(None, False)

    data = summaries.event_summary(rid.runs)
    return render_template('summary_event.html', 
                            data=data)


@app.route('/switch')
@app.route('/switch/<switch_to>', methods=['GET'])
@login_required
def r_switch(switch_to=None):
    return_to = request.args.get('page')
    print('** Came from page: ', return_to)
    
    if not switch_to:
        session['SELECTEDRUNNER'] = {'username': current_user.username, 'rid': current_user.rid}
        return redirect(url_for('runner_runs'))
    
    if switch_to.lower() in [x['f_username'] for x in session['FRIENDS']]:
        user = User.query.filter_by(username=switch_to.lower()).first()
        session['SELECTEDRUNNER'] = {'username': user.username, 'rid': user.rid}
        return redirect(url_for(return_to))
    else:
        return redirect(url_for('error'))
    
    
@app.route('/changepwd')
@login_required
def change_pwd():
    user = User.query.filter_by(username=current_user.username.lower()).first()
    user.email = 'test'
    return redirect(url_for('home'))

    
@app.route('/logout')
def logout():
    logout_user()
    session['SELECTEDRUNNER'] = {'username': None, 'rid': None}
    session['FRIENDS'] = None
    return redirect(url_for('home'))

@app.route('/user')
@login_required
def user_details():
    return render_template('user.html')


# def get_app_title():
#    return os.environ['APP_TITLE'] 

def runapp(host='localhost', port=5000, debug=True):
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    port=5000
    debug=True
    host='localhost'
    runapp(host=host, port=port, debug=debug)
