import hashlib
import random


class Country(object):
    def __init__(self, name, border_countries):
        self.border_countries = border_countries
        self.name = name
        self.owner = None
        self.troops = 0

    def attack(self, country, attacking_troops):
        assert country in self.border_countries
        assert country.owner is not None
        assert country.owner is not self.owner
        assert self.troops - attacking_troops >= 1
        assert attacking_troops > 0
        assert attacking_troops <= 3

        if country.troops >= 2:
            defending_die = 2
        elif country.troops == 1:
            defending_die = 1
        else:
            raise NameError('defending country has no troops')

        if attacking_troops >= 3:
            attacking_die = 3
        elif attacking_troops == 2:
            attacking_die = 2
        elif attacking_troops == 1:
            attacking_die = 1
        else:
            raise NameError('attacking country has no troops')

        defending_rolls = sorted([random.randint(1, 6) for i in range(defending_die)],
                                 reverse=True)
        attacking_rolls = sorted([random.randint(1, 6) for i in range(attacking_die)],
                                 reverse=True)

        for i in range(min(defending_die, attacking_die)):
            if attacking_rolls[i] > defending_rolls[i]:
                country.troops -= 1
            else:
                self.troops -= 1
                attacking_troops -= 1  # Kept track in case of invasion

        if country.troops == 0:
            country.owner = self.owner
            country.troops = attacking_troops
            self.troops -= attacking_troops

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, Country) and self.name == other.name

    def add_troops(self, owner, troops):
        assert owner
        assert owner == self.owner or (self.troops == 0 and self.owner is None)
        assert troops > 0

        if(self.owner is None):
            self.owner = owner
        self.troops += troops


class Continent(object):
    def __init__(self, name, bonus):
        self.name = name
        self.countries = {}
        self.bonus = bonus

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, Continent) and self.name == other.name

    def get_player_set(self):
        print(self.countries)
        return set(country for country in self.countries)


class Board(object):
    def __init__(self):
        self.continents = {}
        self.countries = {}


class Card(object):
    def __init__(self):
        pass


class Player(object):
    def __init__(self, name, base_url):
        self.name = name
        self.cards = set()
        self.is_neutral = False


class World(object):
    def __init__(self, _map, players):
        self._map = map
        self.players = random.shuffle(players)
