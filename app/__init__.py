from flask import Flask, render_template, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.pymongo import PyMongo
from flask.ext.wtf import Form
from flask.ext.wtf.html5 import URLField
from wtforms import TextField, SelectMultipleField
import os
from risk_helper import Player
from risk.models import Players
from risk.game import Game
from start_game import start_risk_game

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or ('sqlite:///' + os.path.join(app.root_path, '../app.db'))
app.secret_key = 'f520d319-8b73-45c1-9982-07e57c0ddaa6'
db = SQLAlchemy(app)
mongo = PyMongo(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    base_url = db.Column(db.String(200), unique=True)

    def __init__(self, username, base_url):
        self.username = username
        self.base_url = base_url

    def __repr__(self):
        return '<User %r @ %r>' % (self.username, self.base_url)

class UserForm(Form):
    username = TextField("Username")
    base_url = URLField("AI URL")

class StartGameForm(Form):
    players = SelectMultipleField("Select Players")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=("GET", "POST"))
def signup():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        base_url = form.base_url.data
        user = User(username, base_url)
        db.session.add(user)
        db.session.commit()
        form = UserForm()
    return render_template("signup.html", form=form)

@app.route("/start-game", methods=("GET", "POST"))
def start_game():
    form = StartGameForm()
    form.players.choices = [(str(user.id), user.username) for user in User.query.all()]
    if form.validate_on_submit():
        print 'got here;'
        user_ids = list(form.players.data)
        if 3 <= len(user_ids) <= 6:
            print user_ids
            users = [(user.username, user.base_url) for user in
                     User.query.filter(User.id.in_(user_ids)).all()]
            start_risk_game.delay(users)
        elif len(user_ids) < 3:
            flash("you need at least 3 players to start a game")
        else:
            flash("you cannont play with more than 6 players")
    return render_template("start-game.html", form=form)

@app.route("/game/<game_id>/<broadcast_count>")
def game(game_id, broadcast_count):
    game = mongo.db.game.find_one_or_404({'uid':game_id, 'broadcast_count':int(broadcast_count)})
    game = {k:game[k] for k in game if k != '_id'}
    return json.dumps(game)
