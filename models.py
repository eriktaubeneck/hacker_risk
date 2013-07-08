import random
import json

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
            return True
        return False

    def add_troops(self, owner, troops):
        assert owner
        assert owner == self.owner or (self.troops == 0 and self.owner is None)
        assert troops > 0

        if(self.owner is None):
            self.owner = owner
        self.troops += troops

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, Country) and self.name == other.name


class Continent(object):
    def __init__(self, name, bonus):
        self.name = name
        self.countries = {}
        self.bonus = bonus

    def get_country_set(self):
        return set([country for country in self.countries])

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, Continent) and self.name == other.name

    def get_player_set(self):
        keys = self.countries.keys()
        return set([self.countries[key].owner for key in keys])


class Board(object):
    def __init__(self):
        self.continents = {}
        self.countries = {}


class Card(object):
    def __init__(self, country, value):
        self.country = country
        self.value = value

    def is_set_with(self, card_two, card_three):
        assert card_two is not None
        assert card_three is not None
        wild_cards = [card for card in list(self, card_two, card_three) if card.value == "wild"]
        return (len(wild_cards) >= 1) or (self.value == card_two.value == card_three.value) or (self.value != card_two.value != card_three.value)


class Player(object):
    def __init__(self, name):
        self.name = name
        self.cards = set()
        self.is_eliminated = False
        self.is_neutral = False
        self.countries = set()
        self.earned_card_this_turn = False

    def choose_country(self, country):
        assert country.owner is None
        self.countries.add(country)
        country.owner = self
        self.deploy_troops(country,1)

    def deploy_troops(self, country, troops):
        assert country.owner is self
        country.troop += troops

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, Player) and self.name == other.name


class World(object):
    def __init__(self, _map, players):
        self._map = _map
        self.players = random.shuffle(players)


def import_board_data(json_url):
    board_file = open(json_url)
    board_json = json.load(board_file)
    board_file.close()
    board = Board()
    countries = {}
    cards = []
    #go through the json and create the list of countries
    for continent_name in board_json:
        board.continents[continent_name] = Continent(continent_name,

board_json[continent_name]["bonus"])
        for country_name in board_json[continent_name]["countries"]:
            countries[country_name] = Country(country_name,

board_json[continent_name]["countries"][country_name]["border countries"])
            cards.append(Card(countries[country_name],                              board_json[continent_name]["countries"][country_name]["card"]))
            board.continents[continent_name].countries[country_name] =                     countries[country_name]
    #loop through the country list and replace all of the border country strings with      references to that country
    for country_name in countries:
        borders = [countries[name] for name in countries[country_name].border_countries]
        countries[country_name].border_countries = borders
    board.countries = countries
    #add the two wild cards
    cards.append(Card(None, "wild"))
    cards.append(Card(None, "wild"))
    #return a tuple with the board and the cards
    return board, cards
