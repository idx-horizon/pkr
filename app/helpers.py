from app import db
from app.models import User

def seticon():
     users = [('ian',     '🔴'),
          ('michael', '🏃‍♂️'),
          ('same',    '🏃‍♂️'),
          ('ant',     '🏃‍♂️'),
          ('matt',    '🏃‍♂️'),
          ('caroline','✨')
     ]
     for u in users:
          x = User.query.filter_by(username=u[0].first()
          x.icon = x[1]
          db.session.commit()
