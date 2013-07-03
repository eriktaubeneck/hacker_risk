import models
import mapgen

board = mapgen.generate_board()
players = []

players.append(models.Player('Erty', None))
players.append(models.Player('Alex', None))

Alaska = board.countries['alaska']
Northwest_Territory = board.countries['northwest territory']

Alaska.owner = players[0]
Northwest_Territory.owner = players[1]

Alaska.troops = 30
Northwest_Territory.troops = 10

while Alaska.owner != Northwest_Territory.owner and Alaska.troops > 1:
    Alaska.attack(Northwest_Territory, min(Alaska.troops, 3))
    print("Alaska: " + Alaska.owner.name + " : " + str(Alaska.troops))
    print("NWTerr: " + Northwest_Territory.owner.name + " : " + str(Northwest_Territory.troops))
    print("---")
