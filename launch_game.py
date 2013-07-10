from risk_helper import Player
from risk.models import Players
from risk.game import Game

player1_name = 'player 1'
player1_url = 'http://localhost:4444'
player2_name = 'player 2'
player2_url = 'http://localhost:4445'
player3_name = 'player 3'
player3_url = 'http://localhost:4446'

players = Players([Player(player1_name, player1_url),
                   Player(player2_name, player2_url),
                   Player(player3_name, player3_url)])

game = Game(players)

game.start_game()
