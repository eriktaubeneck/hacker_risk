import game 
import unittest
import random
import models
from mock import patch
from models import Players

class TestGame(unittest.TestCase):
    def setUp(self):
        self.players = Players()
        self.players.add_player(models.Player('Erik'))
        self.players.add_player(models.Player('Erty'))
        self.players.add_player(models.Player('Alex'))
        self.game = game.Game(self.players)

    def test_deployment_phase(self):
        pass

    def test_attacking_phase(self):
        pass

    def test_reinforce(self):
        pass
    
    def test_check_winner(self):
        pass

    def test_elimination(self):
        alex = self.players[2]
        erty = self.players[1]
        self.game.eliminate_player(alex, erty)
        self.assertEqual(erty.is_eliminated, True)

    def test_trade_cards_for_troops(self):
        pass
    
    def test_init_deploy(self):
        pass

    def test_play_game(self):
        pass

    def test_start(self):
        pass
        #self.game.start_game()
