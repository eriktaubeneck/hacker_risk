import game 
import unittest
import random
import models
from mock import patch
from players import Players

class TestGame(unittest.TestCase):
    def setUp(self):
        players = Players([models.Player('Erik'), models.Player('Erty'), models.Player('Alex')])
        self.game = game.Game(players)

    def test_start(self):
        pass
        #self.game.start_game()


