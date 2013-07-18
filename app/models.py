from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    base_url = db.Column(db.String(200), unique=True)

    def __init__(self, username, base_url):
        self.username = username
        self.base_url = base_url

    def __repr__(self):
        return '<User %r @ %r>' % (self.username, self.base_url)
