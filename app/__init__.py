from flask import Flask, render_template, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form
from flask.ext.wtf.html5 import URLField
from wtforms import TextField
import os
from risk_helper import Player
from risk.models import Players
from risk.game import Game

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or ('sqlite:///' + os.path.join(app.root_path, '../app.db'))
app.secret_key = 'f520d319-8b73-45c1-9982-07e57c0ddaa6'
db = SQLAlchemy(app)

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

@app.route("/start_game")
def start_game():
    player_list = [] # Need to load this from form arguments.
    players = Players()
    for player_info in player_list: # player_info is tuple (player_name, player_url).
        player = Player(player_info[0], player_info[1])
        Players.add_player(player)
    game = Game(players)
    Game.start_game()


