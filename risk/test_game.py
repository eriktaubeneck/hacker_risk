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
        self.players.start_game()

    def test_deployment_phase(self):
        country_A = self.game.board.countries["alaska"]
        country_A.owner = self.players.current_player
        #TODO: finish this test...

    def test_attacking_phase(self):
        country_A = self.game.board.countries["northwest territory"]
        country_B = self.game.board.countries["alaska"]
        country_A.owner = self.players.current_player
        country_B.owner = models.Player("bob")
        country_A.troops = 10
        country_B.troops = 5
        with patch.object(Players, "attack") as mock_attack, patch.object(random, 'randint') as mock_random:
            mock_attack.return_value = [country_A, country_B, 3, 3]
            mock_random.side_effect = [6,6,1,1,1]
            self.game.attacking_phase()
            self.assertEqual(country_A.troops, 8)
            self.assertEqual(country_B.troops, 5)

    def test_reinforce(self):
        country_A = self.game.board.countries["northwest territory"] 
        country_B = self.game.board.countries["alaska"]
        country_A.owner = self.players.current_player
        country_A.troops = 10
        country_B.troops = 5
        country_B.owner = self.players.current_player
        with patch.object(Players, 'reinforce') as mock_method:
            mock_method.return_value = [country_A, country_B, 2]
            self.game.reinforce()
            self.assertEqual(country_A.troops, 8)
            self.assertEqual(country_B.troops, 7)
    
    def test_check_winner(self):
        pass

    def test_elimination(self):
        alex = self.players[2]
        erty = self.players[1]
        self.game.eliminate_player(alex, erty)
        self.assertEqual(erty.is_eliminated, True)

    def test_trade_cards_for_troops(self):
        cards = [models.Card("country_A", "whiskey"), models.Card("country_B", "gin"), models.Card("country_C", "tequila")]
        self.players.current_player.cards = set(cards)
        trade_1_troops = self.game.get_troops_for_card_set(cards)
        self.assertEqual(trade_1_troops, 4)
        self.players.current_player.cards = set(cards)
        trade_2_troops = self.game.get_troops_for_card_set(cards)
        self.assertEqual(trade_2_troops, 6)
        cards2 = [models.Card("cowLand", "cow"), models.Card("mexico", "horse"), models.Card("canada", "horse")]
        self.players.current_player.cards = set(cards2)
        with self.assertRaises(AssertionError):
            trade_3_troops = self.game.get_troops_for_card_set(cards2)
    
    def test_init_deploy(self):
        pass

    def test_play_game(self):
        pass

    def test_start(self):
        pass
        #self.game.start_game()
