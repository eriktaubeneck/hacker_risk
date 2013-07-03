import models
import mapgen
import unittest
import random

class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = mapgen.generate_board()
        self.players = [models.Player('Erty'),models.Player('Alex')]
        self.Alaska = board.countries['alaska']
        self.Northwest_Territory = board.countries['northwest territory']
        

board = mapgen.generate_board()
players = []

players.append(models.Player('Erty', None))
players.append(models.Player('Alex', None))

Alaska = board.countries['alaska']
Northwest_Territory = board.countries['northwest territory']

Alaska.add_troops(players[0], 30)
Northwest_Territory.add_troops(players[1], 10)

assert(Alaska.owner == players[0])
assert(Northwest_Territory.owner == players[1])

#while Alaska.owner != Northwest_Territory.owner and Alaska.troops > 1:
#    Alaska.attack(Northwest_Territory, min(Alaska.troops, 3))
#    print("Alaska: " + Alaska.owner.name + " : " + str(Alaska.troops))
#    print("NWTerr: " + Northwest_Territory.owner.name + " : " + str(Northwest_Territory.troops))
#    print("---")

print(board.continents)

print(board.continents['north america'].get_player_set())
