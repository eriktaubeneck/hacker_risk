import models
import unittest
import random
from mock import patch
from players import Players

class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board, self.cards = models.import_board_data('./board_graph.json')

    def test_border_countries(self):
        country_A = self.board.countries['alaska']
        country_B = self.board.countries['northwest territory']
        self.assertIn(country_A, country_B.border_countries)
        self.assertIn(country_B, country_A.border_countries)

    def test_not_border_countries(self):
        country_A = self.board.countries['iceland']
        country_B = self.board.countries['northwest territory']
        self.assertNotIn(country_A, country_B.border_countries)
        self.assertNotIn(country_B, country_A.border_countries)


    def test_add_troops(self):
        country_A = self.board.countries['iceland']
        country_B = self.board.countries['northwest territory']
        erty = models.Player('Erty')
        country_A.owner = erty
        country_A.troops = 20
        country_A.add_troops(erty, 10)
        country_B.add_troops(erty, 10)
        self.assertEqual(country_A.troops, 30)
        self.assertEqual(country_B.troops, 10)


    def test_attack(self):
        country_A = self.board.countries['alaska']
        country_B = self.board.countries['northwest territory']
        players = Players([models.Player('Erty'),models.Player('Alex')])
        country_A.owner = players[0]
        country_B.owner = players[1]
        country_A.troops = 30
        country_B.troops = 10
        with patch.object(random, 'randint') as mock_method:
            mock_method.side_effect = [6,6,1,1,1]
            country_A.attack(country_B, 3)
            self.assertEqual(country_A.troops, 28)
            self.assertEqual(country_B.troops, 10)


        with patch.object(random, 'randint') as mock_method:
            mock_method.side_effect = [1,1,6,6,6]
            country_A.attack(country_B,3)
            self.assertEqual(country_A.troops, 28)
            self.assertEqual(country_B.troops, 8)

    def test_get_player_set(self):
        country_A = self.board.countries['alaska']
        country_B = self.board.countries['northwest territory']
        players = [models.Player('Erty'),models.Player('Alex')]
        country_A.owner = players[0]
        country_B.owner = players[1]
        player_set = self.board.continents['north america'].get_player_set()
        self.assertEqual(len(player_set), 3)

    def test_cards(self):
        pass
