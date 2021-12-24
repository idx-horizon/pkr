from app import db
from app.models import User, Friend, LoginLog

def clearlog():
     LoginLog.clear_log()
     
def seticon(who,value):
     x = User.query.filter_by(username=who).first()
     x.icon = value
     db.session.commit()
     
def seticon_all():
     users = [('ian', '🆔', 47.5, 'av_ian.jpg'),
          ('michael', 'Ⓜ️', 50.0, 'av_michael.jpg'),
          ('sam',     '🏃‍♂️', 50.0, 'av_default.jpg'),
          ('ant',     '👨', 50.0, 'av_default.jpg'),
          ('matt',    'Ⓜ️', 50.0, 'av_default.jpg'),
          ('eileen',  '🙎‍♀️', 50.0, 'av_default.jpg'),
          ('sharon',  '🙎‍♀️', 50.0, 'av_default.jpg'),
          ('caroline','✨', 50.0, 'av_caroline.jpg'),
          ('norm',    '🏃‍♂️', 50.0, 'av_default.jpg'),
          ('cat',     '😼', 50.0, 'av_cat.jpg')          
     ]
     
     for u in users:
          x = User.query.filter_by(username=u[0]).first()
          x.icon = u[1]
          x.agegrade_theshold = u[2]
          x.avatar = u[3]
          db.session.commit()

def add_f(f, t):
     to = User.query.filter_by(username=t).first()
     friend = Friend(f_username=t,f_rid=to.rid, u_username=f)
     db.session.add(friend)
     db.session.commit()

def all_u():
     users = User.query.all()
     for u in users: 
          print('{:<10} {:<8} {:<15} {:<5} {:<6} {}'.format(
               u.username, 
               u.rid, 
               u.home_run, 
               str(u.is_admin), 
               str(u.agegrade_theshold),
               u.avatar))
               
def agegrade(u,value):
     to = User.query.filter_by(username=u).first()
     to.agegrade_theshold = value
     db.session.commit()
