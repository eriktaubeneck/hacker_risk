import models
import mapgen

themap = mapgen.generateMap()
players = []

players.append(models.Player('Erty'))
players.append(models.Player('Alex'))

Alaska = themap.countries[0]
Northwest_Territory = themap.countries[1]

Alaska.owner = players[0]
Northwest_Territory.owner = players[1]

Alaska.troops = 30
Northwest_Territory.troops = 10
