from app import db
from app.models import User

def seticon():
     users = [('ian', '🆔'),
          ('michael', '🏃‍♂️'),
          ('sam',     '🏃‍♂️'),
          ('ant',     '🏃‍♂️'),
          ('matt',    '🏃‍♂️'),
          ('caroline','✨')
     ]
     
     for u in users:
          x = User.query.filter_by(username=u[0]).first()
          x.icon = u[1]
          db.session.commit()
