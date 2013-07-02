import hashlib
import random

class Country(object):
    def __init__(self):
        self.boarder_countries = []

    def set_continent(self,continent):
        self.continent = continent
        self.contient.countries.add(self)

class Continent(object):
    def __init__(self):
        self.countries = set()

class Map(object):
    def __init__(self):
        self.continents = set()
        self.countries = set()
        
    def add_continent(self,continent):
        self.continents.add(continent)
        self.countries.union(continent.countries)

class Card(object):
    def __init__(self):
        pass

class Player(object):
    def __init__(self, base_url):
        self.base_url = base_url
        self.key = hashlib.md5().hexdigest()
        self.errors = 0
        self.cards = set()
        self.is_neutral = False

class World(object):
    def __init__(self, _map, players):
        self._map = map
        self.players = random.shuffle(players)
