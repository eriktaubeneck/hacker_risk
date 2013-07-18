from celery import Celery
from risk.models import Players
from risk_helper import Player
from risk.game import Game


celery = Celery('tasks', backend='amqp', broker='amqp://guest@localhost//')

@celery.task
def start_risk_game(user_ids):
    players = Players()
    for user_id in user_ids:
        user = User.query.filter(User.id == user_id).one()
        players.add_player(Player(user.username, user.base_url))
    game = Game(players)
    game.start_game()

from app.models import User
