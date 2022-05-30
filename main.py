import os
from flask import Flask, jsonify, abort, flash, make_response, render_template, redirect, request, url_for, session
from flask_login import login_user, logout_user, current_user, login_required, UserMixin

from operator import attrgetter
from werkzeug.urls import url_parse
from collections import Counter

from app import app, login, db

from app.track import Tracker
from app.models import User, Country, Location, LoginLog, Friend
from app.forms import LoginForm
from app.resources import country_dict, centres
import app.newruns as NR
import app.utils as utils
import app.summaries as summaries
import datetime
import pandas as pd

import pygal


@app.route("/xltables")
def show_tables():
    data = pd.read_excel('static/dummy.xlsx')
    data.set_index(['Name'], inplace=True)
    data.index.name = None
    females = data.loc[data.Gender == 'f']
    males = data.loc[data.Gender == 'm']
    return render_template('xlview.html',
                           tables=[females.to_html(classes='female'),
                                   males.to_html(classes='male'),
                                   data.to_html(classes='all')
                                   ],
                           titles=['na', 'Female', 'Male', 'All'])


app_TRACKER = Tracker()


def reset_session_selectedrunner():
    session['SELECTEDRUNNER'] = {
        'username': None,
        'rid': None,
        'threshold': None,
        'icon': None,
        'avatar': None,
        'friend_list': None,
        'runner': None,
        'me_summary': None}


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Friend': Friend}


@app.context_processor
def inject_context():
    try:
        return dict(selected_runner=session['SELECTEDRUNNER'],
                    friends=session['FRIENDS'],
                    title=os.environ['APP_TITLE'])
    except Exception as e:
        print('** inject_context Error: {}'.format(e))
        logout_user()
        reset_session_selectedrunner()
        session['FRIENDS'] = None
        return redirect(url_for('home'))


@app.template_filter()
def format_datetime(
        value, format_src='%d/%m/%Y', format_out='%d-%b-%Y'):
    try:
        x = datetime.datetime.strptime(value, format_src)
        return x.strftime(format_out)
    except:
        return value


@app.errorhandler(404)
def error_404(error):
    try:
        print('URL request: {}'.format(request))
    except:
        pass
    print('** 404 Error: {}'.format(error))
    return redirect('/error/404')


@app.errorhandler(500)
def error_500(error):
    print('** 500 Error: {}'.format(error))
    return redirect('/login')


#    return redirect('/error/500')

@app.route('/error/')
@app.route('/error/<code>')
def error(code=None):
    return render_template('error.html', error_code=code)


@app.route('/')
def index():
    return redirect('/home/')


@app.route('/api/v1/meta', methods=['POST', 'GET'])
def apilog():
    global app_TRACKER

    app_TRACKER.update(request)

    payload = app_TRACKER.meta

    if request.method.upper() == 'POST':
        return jsonify(payload)
    else:
        return render_template('apilog.html', payload=payload)

@app.route('/graphbar')
def r_graph1():

    SELECTEDRUNNER = session['SELECTEDRUNNER']
    rid = utils.Runner(SELECTEDRUNNER['rid'] or current_user.rid)

    rid.get_runs(None, False)

    graph = pygal.Line(style=pygal.style.LightGreenStyle)

    graph.title = 'Test Graph'
    current_series = [10,21,13,16]
    graph.add(SELECTEDRUNNER['username'].title(),
                  current_series,
                  dots_size=1)
    
    graph_data = graph.render_data_uri()
    return render_template("graph.html",
                           graph_title=graph.title,
                           graph_data=graph_data)

@app.route('/graph')
@app.route('/graph/')
def r_graph():
    graphtype = request.args.get('graphtype', 'runtime')
    print('GRAPH TYPE: {}'.format(graphtype))
    if graphtype == 'agegrading':
        params = ('AgeGrade', [25, 75], '%', '', 1, 'Age Grading')
    elif graphtype == 'runtime':
        params = ('TimeSecs', [15, 40], ':', '.', 60, 'Run Time')

    SELECTEDRUNNER = session['SELECTEDRUNNER']
    rid = utils.Runner(SELECTEDRUNNER['rid'] or current_user.rid)

    rid.get_runs(None, False)
    mx_runs = 50

    if current_user.rid != SELECTEDRUNNER['rid']:
        me = utils.Runner(current_user.rid)
        me.get_runs(None, False)

    try:
        graph = pygal.Line(style=pygal.style.LightGreenStyle)

        graph.title = '{} over last {} runs'.format(params[5], mx_runs)
        subset = reversed(list(rid.runs[:mx_runs]))
        current_series = [float(str(x[params[0]]).replace(params[2], params[3])) / params[4] for x in subset]
        graph.add(SELECTEDRUNNER['username'].title(),
                  current_series,
                  dots_size=1)
        my_series = current_series
        if current_user.rid != SELECTEDRUNNER['rid']:
            my_series = [float(str(x[params[0]]).replace(params[2], params[3])) / params[4] for x in
                         reversed(list(me.runs[:mx_runs]))]
            graph.add(current_user.username.title(),
                      my_series,
                      dots_size=1)

        graph.range = [min(current_series + my_series) - 1,
                       max(current_series + my_series) + 1]

        graph_data = graph.render_data_uri()
        return render_template("graph.html",
                               graph_title=graph.title,
                               graph_data=graph_data)
    except Exception as e:
        return (str(e))


@app.route('/home/')
def home():
    return render_template('home.html',
                           file_modified_date=NR.get_last_update())


@app.route('/events/', methods=['POST', 'GET'])
def r_events():
    this_country = 'uk'
    this_filter = ''
    this_method = 'startswith'
    this_has_run = 'all'

    if not current_user.is_anonymous:
        this_centre_on = current_user.home_run
    else:
        this_centre_on = 'bushy'

    if request.method.upper() == 'POST':
        this_filter = str(request.form['filter_str']).lower()
        this_method = str(request.form['filter_method'])
        this_country = str(request.form['country_code'])
        this_centre_on = str(request.form['centre_on_code'])
        this_has_run = str(request.form['has_run'])

    data = NR.getevents_by_filter(this_filter, country_dict[this_country]['id'], this_method, this_centre_on)
    data = sorted(data, key=attrgetter('distance'))

    if not current_user.is_anonymous:
        SELECTEDRUNNER = session['SELECTEDRUNNER']
        base_runner = SELECTEDRUNNER['rid'] or current_user.rid
        rid = utils.Runner(str(base_runner).lower())
        rid.get_runs(this_filter, False)

        for d in data:
            occ = len([x for x in rid.runs if x['Event'] == d.evshortname])
            d.set_occurrences(occ)
            if occ != 0:
                d.set_hasrun('Yes')

        if this_has_run == 'never':
            data = [d for d in data if d.occurrences == 0]
        elif this_has_run == 'singleton':
            data = [d for d in data if d.occurrences == 1]
        elif this_has_run == 'any':
            data = [d for d in data if d.occurrences > 0]

    return render_template('events.html',
                           filter=this_filter,
                           filter_method=this_method,
                           file_modified_date=NR.get_last_update(),
                           countries=country_dict,
                           country=this_country,
                           centres=centres.keys(),
                           centre_on=this_centre_on,
                           has_run=this_has_run,
                           data=data)


@app.route('/stats', methods=['POST', 'GET'])
@app.route('/stats/', methods=['POST', 'GET'])
@login_required
def runner_stats():
    SELECTEDRUNNER = session['SELECTEDRUNNER']
    rid = utils.Runner(SELECTEDRUNNER['rid'] or current_user.rid)

    rid.get_runs(None, False)
    rid.updated_dt = rid.updated_dt.strftime('%d-%b-%Y %H:%M')

    return render_template('stats.html',
                           file_modified_date=NR.get_last_update(),
                           data=rid)


@app.route('/atoz', methods=['GET'])
@app.route('/atoz/', methods=['GET'])
@login_required
def r_atoz():
    cid_data = None
    sid_data = None
    runner_names = []
    event_counts = []
    
    SELECTEDRUNNER = session['SELECTEDRUNNER']
    sid = utils.Runner(SELECTEDRUNNER['rid'] or current_user.rid)
    sid.get_runs(None,False)
    sid_data = sid.atoz()
    event_counts.append(sum([len(sid_data[x]) for x in sid_data]))
    runner_names.append(sid.name)
    
    if current_user.rid != SELECTEDRUNNER['rid']:
        cid = utils.Runner(current_user.rid)
        cid.get_runs(None, False)
        cid_data = cid.atoz()
        event_counts.append(sum([len(cid_data[x]) for x in cid_data]))
        runner_names.append(cid.name)
        
    return render_template('atoz.html', 
                            runner_names=runner_names,
                            event_counts=event_counts,
                            cid_data=cid_data,
                            sid_data=sid_data)

@app.route('/headtohead', methods=['POST', 'GET'])
@app.route('/headtohead', methods=['POST', 'GET'])
@login_required
def r_headtohead(params=None):
    try:
        against_rid = str(request.form['against'])
    except:
        against_rid = session['FRIENDS'][0]['f_rid']

    # get selectd against_rid runner's detail
    srid = utils.Runner(against_rid)
    srid.get_runs('', False, 'Date')

    # get currently logged in user details
    crid = utils.Runner(current_user.rid)
    crid.get_runs('', False, 'Date')

    data = {}
    lastsat = utils.last_saturday()
    for i in range(20):
        dt = lastsat - datetime.timedelta(days=i * 7)
        fdt = dt.strftime('%d/%m/%Y')
        c1 = [(e['Event'], e['Time']) for e in crid.runs if e['Run Date'] == fdt]
        c2 = [(e['Event'], e['Time']) for e in srid.runs if e['Run Date'] == fdt]
        if len(c1) == 0:
            c1 = [('', '')]
        if len(c2) == 0:
            c2 = [('', '')]
        data[fdt] = [c1[0], c2[0]]

    return render_template('headtohead.html',
                           data=data,
                           runner_names=[crid.name, srid.name],
                           selectedrunner=against_rid,
                           )


@app.route('/runs', methods=['POST', 'GET'])
@app.route('/runs/', methods=['POST', 'GET'])
@app.route('/runs/<params>/', methods=['POST', 'GET'])
@login_required
def runner_runs(params=None):
    SELECTEDRUNNER = session['SELECTEDRUNNER']
    rid = utils.Runner(SELECTEDRUNNER['rid'] or current_user.rid)

    this_filter = params or ''
    try:
        this_sort = str(request.form['sort_by'])
    except:
        this_sort = 'Date'

    if request.method.upper() == 'POST':
        this_filter = str(request.form['filter_str']).lower()
        this_sort = str(request.form['sort_by'])

    print('** [{}] - [{}] - [{}]'.format(this_filter, this_sort, params))
    rid.get_runs(this_filter, False, this_sort)
    rid.updated_dt = rid.updated_dt.strftime('%d-%b-%Y %H:%M')

    return render_template('runs.html',
                           file_modified_date=NR.get_last_update(),
                           data=rid,
                           filter=this_filter,
                           sortcol=this_sort,
                           threshold='{:05.2f}'.format(SELECTEDRUNNER['threshold']))


@app.route('/loginlog/', methods=['POST', 'GET'])
def r_loginlog():
    white_ips = [x for x in os.environ.get('MY_IP_WHITELIST', '').split('|') if x != '']
    data = LoginLog.get_log(lmt=20, white_ips=white_ips)
    return render_template('loginlog.html', data=data)


@app.route('/newevents/', methods=['POST', 'GET'])
@app.route('/newevents/<country>/', methods=['POST', 'GET'])
@app.route('/newevents/<country>/<limit>/', methods=['POST', 'GET'])
def r_newevents(limit=10, country=None):
    this_limit = int(limit) or 15
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


@app.route('/login/', methods=['POST', 'GET'])
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

        runner = utils.Runner(user.rid or current_user.rid)
        runner.get_runs(None, False)
        summary = runner.get_card_summary()

        session['SELECTEDRUNNER'] = {
            'username': user.username,
            'rid': user.rid,
            'threshold': user.agegrade_theshold,
            'icon': user.icon,
            'avatar': user.avatar,
            'number_of_runs': len(runner.runs),
            'friend_list': {},
            'runner': summary,
            'me_summary': summary
        }
        print('*** Session:', session['SELECTEDRUNNER'])
        session['FRIENDS'] = Friend.get(user.username)
        for f in Friend.get(user.username):
            session['SELECTED_RUNNER']['friend_list'][f] = -1

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


@app.route('/switch', methods=['GET'])
@app.route('/switch/<switch_to>', methods=['GET'])
@login_required
def r_switch(switch_to=None):
    return_to = request.args.get('page')
    print('** Came from page: ', return_to)
    me_summary = session['SELECTEDRUNNER']['me_summary']
    if not switch_to:
        runner = utils.Runner(current_user.rid)
        runner.get_runs(None, False)
        summary = runner.get_card_summary()

        session['SELECTEDRUNNER'] = {
            'username': current_user.username,
            'rid': current_user.rid,
            'threshold': current_user.agegrade_theshold,
            'icon': current_user.icon,
            'avatar': current_user.avatar,
            'friend_list': [],
            'runner': summary,
            'me_summary': me_summary
        }
        return redirect(url_for(return_to))

    if switch_to.lower() in [x['f_username'] for x in session['FRIENDS']]:
        user = User.query.filter_by(username=switch_to.lower()).first()

        runner = utils.Runner(user.rid)
        runner.get_runs(None, False)
        summary = runner.get_card_summary()

        session['SELECTEDRUNNER'] = {
            'username': user.username,
            'rid': user.rid,
            'threshold': user.agegrade_theshold,
            'icon': user.icon,
            'avatar': user.avatar,
            'friend_list': [],
            'runner': summary,
            'me_summary': me_summary
        }
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
    reset_session_selectedrunner()
    session['FRIENDS'] = None
    return redirect(url_for('home'))


@app.route('/user')
@login_required
def user_details():
    return render_template('user.html')


@app.route('/image')
def r_image():
    return render_template('image.html')


# def get_app_title():
#    return os.environ['APP_TITLE'] 

def runapp(host='localhost', port=5000, debug=True):
    print('** MY PARAMS: {}'.format(os.environ['MY_PARAMS']))
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    port = 5000
    debug = True
    host = 'localhost'
    runapp(host=host, port=port, debug=debug)
