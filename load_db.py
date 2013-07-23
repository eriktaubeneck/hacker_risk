from app import db
from app.models import *

db.drop_all()
db.create_all()
db.session.commit()

db.session.add(User('aqueous-retreat', 'http://aqueous-retreat-6299.herokuapp.com'))
db.session.add(User('still-sierra', 'http://still-sierra-4691.herokuapp.com'))
db.session.add(User('pacific-wildwood', 'http://pacific-wildwood-2067.herokuapp.com'))

db.session.commit()
