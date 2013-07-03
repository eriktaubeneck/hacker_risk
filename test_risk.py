import models
import mapgen
import unittest
import random



class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = mapgen.generate_board()
                
    def test_border_countries(self):
        country_A = board.countries['alaska']
        country_B = board.countries['northwest territory']
        self.assertIn(country_A, country_B.border_countries)
        self.assertIn(country_B, country_A.border_countries)

    def test_not_border_countries(self):
        country_A = board.countries['iceland']
        country_B = board.countries['northwest territory']
        self.assertIn(country_A, country_B.border_countries)
        self.assertIn(country_B, country_A.border_countries)
        
    def test_attack(self):
        country_A = board.countries['alaska']
        country_B = board.countries['northwest territory']
        players = [models.Player('Erty'),models.Player('Alex')]
        country_A.owner = players[0]
        country_B = players[1]
        country_A.troops = 30
        country_B.troops = 10
        with patch.object(random, 'randint') as mock_method:
            mock_method.return_value = 6
            country_A.attack(country_B, 3)
            self.assertEqual(country_A, 28)
            self.assertEqual(country_B, 10)

