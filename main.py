import os
from flask import Flask
from flask import Flask, jsonify, abort, flash, make_response, render_template, redirect, request, url_for, session

from app import app,login
from app.forms import LoginForm
from flask_login import UserMixin

import app.newruns as NR

from flask_login import login_user, logout_user, current_user, login_required, UserMixin

class User(UserMixin):
    def __init__(self, id):
        self.id = id
    def get(self):
        return 'ian'

@login.user_loader
def load_user(id):
    return User.get(id)

@app.errorhandler(404)
def error_404(error):
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
    return render_template('home.html')

    
@app.route('/startswith/')
@app.route('/startswith/<prefix>')
def starts(prefix='z'):
    this_prefix = prefix or 'z'
    data=NR.getevents_by_prefix(prefix)
    file_modified_date = NR.get_last_update()
    return render_template('startswith.html',
                app_name='WIP',
                title='wip', 
                prefix=this_prefix, 
                file_modified_date=file_modified_date,
                data=data)
    
@app.route('/newruns/')
@app.route('/newruns/<limit>')
def newruns(limit=10):
    title = os.environ['USER_NAME'] + '(' + os.environ['APP_NAME'] + ')'
    this_limit =int(limit) or 10
    data = NR.get_last_newruns(this_limit)
    file_modified_date = NR.get_last_update()
    return render_template('newruns.html',
                title=title, 
                limit=this_limit, 
                file_modified_date=file_modified_date,
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


def runapp(host='localhost', port=5000, debug=True):
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    port=5000
    debug=True
    host='localhost'
    runapp(host=host, port=port, debug=debug)
