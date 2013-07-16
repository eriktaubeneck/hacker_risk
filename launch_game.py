from risk_helper import Player
from risk.models import Players
from risk.game import Game
import sys

n_players = int(sys.argv[1])
first_port = 4444

players = Players()
for i in range(n_players):
    players.add_player(Player('player %s' % i, 'http://localhost:%s' % (first_port+1)))

game = Game(players)

game.start_game()
