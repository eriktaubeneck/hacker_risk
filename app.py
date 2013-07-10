from flask import Flask, render_template
from risk_helper import Player
from risk.models import Players
from risk.game import Game

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add_player")
def add_player():
    return render_template("add_player.html")

@app.route("/start_game")
def start_game():
    player_list = [] # Need to load this from form arguments.
    players = Players()
    for player_info in player_list: # player_info is tuple (player_name, player_url).
        player = Player(player_info[0], player_info[1])
        Players.add_player(player)
    game = Game(players)
    Game.start_game()


