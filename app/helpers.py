from app import db
from app.models import User

u = User.query.filter_by(username='ian').first()
u.icon = '🔴'
db.session.commit()
u = User.query.filter_by(username='michael').first()
u.icon = '🏃‍♂️'
db.session.commit()
u = User.query.filter_by(username='caroline').first()
u.icon = '🏃‍♀️'
db.session.commit()
