from celery import Celery
from risk.game import Game as RiskGame

celery = Celery('tasks', backend='amqp', broker='amqp://guest@localhost//')

@celery.task
def start_risk_game(user_ids, game_id):
    players = Players()
    for user_id in user_ids:
        user = User.query.filter(User.id == user_id).one()
        players.add_player(Player(user.username, user.base_url))
    risk_game = RiskGame(players)
    game = db.session.query(Game).filter(Game.id == game_id).one()
    print game_id
    print game
    game.uid = str(risk_game.uid)
    game.is_running = True
    db.session.add(game)
    db.session.commit()
    risk_game.start_game()
    game.is_running = False
    game.completed = True
    if risk_game.winner:
        game.winner = User.query.filter(User.username == risk_game.winner).one()
    game.broadcast_count = risk_game.broadcast_count
    db.session.add(game)
    db.session.commit()

from app import db
from app.models import User, Game
from risk_helper import Player, Players
