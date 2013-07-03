import models
import mapgen

board = mapgen.generate_board()
players = []

players.append(models.Player('Erty'))
players.append(models.Player('Alex'))

Alaska = board.countries['alaska']
Northwest_Territory = board.countries['northwest territory']

Alaska.owner = players[0]
Northwest_Territory.owner = players[1]

Alaska.troops = 23
Northwest_Territory.troops = 1
