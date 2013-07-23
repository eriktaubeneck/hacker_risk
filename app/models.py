from app import db

game_user_table = db.Table('game_user', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('game_id', db.Integer, db.ForeignKey('game.id'))
)

completed_game_user_table = db.Table('completed_game_user', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('game_id', db.Integer, db.ForeignKey('game.id'))
)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    base_url = db.Column(db.String(200), unique=True)
    games = db.relationship("Game",
                            secondary=game_user_table,
                            backref="users")
    completed_games = db.relationship("Game",
                                      secondary=completed_game_user_table,
                                      backref="completed_users")
    games_won = db.relationship("Game", backref='winner')

    def __init__(self, username, base_url):
        self.username = username
        self.base_url = base_url

    def __repr__(self):
        return '<User %r @ %r>' % (self.username, self.base_url)

class Game(db.Model):
    __tablename__ = 'game'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(50), unique=True)
    is_running = db.Column(db.Boolean)
    completed = db.Column(db.Boolean)
    winner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    broadcast_count = db.Column(db.Integer)

    def __init__(self):
        self.is_running = False
        self.completed = False
