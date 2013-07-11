import random
import json
import itertools

class Country(object):
    def __init__(self, name, border_countries):
        self.border_countries = border_countries
        self.name = name
        self.owner = None
        self.troops = 0

    def attack(self, country, attacking_troops, moving_troops):
        assert country in self.border_countries
        assert country.owner is not None
        assert country.owner is not self.owner
        assert self.troops - (attacking_troops + moving_troops) >= 1
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
            country.owner.countries.remove(country)
            self.owner.countries.add(country)
            country.owner = self.owner
            country.troops = attacking_troops + moving_troops
            self.troops -= attacking_troops
            return True
        return False

    def add_troops(self, owner, troops):
        assert owner
        assert owner == self.owner or (self.troops == 0 and self.owner is None)
        assert troops > 0

        if(self.owner is None):
            self.owner = owner
            self.owner.countries.add(self)
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
        self.cards = {}


class Card(object):
    def __init__(self, country_name, value):
        self.country_name = country_name
        self.value = value

    def is_set_with(self, card_two, card_three):
        assert card_two is not None
        assert card_three is not None
        wild_cards = [card for card in [self, card_two, card_three] if card.value == 'wild']
        return (len(wild_cards) >= 1) or (self.value == card_two.value == card_three.value) or (self.value != card_two.value != card_three.value)


class Player(object):

    def __init__(self, name):
        self.name = name
        self.cards = set()
        self.is_eliminated = False
        self.is_neutral = False
        self.countries = set()
        self.earned_card_this_turn = False
        self.troops_to_deploy = 0
        self.available_actions = []
        self.errors = 0

    def choose_country(self, country):
        assert country.owner is None
        country.add_troops(self,1)

    def deploy_troops(self, country, troops):
        country.add_troops(self,troops)

    def check_neutralized(self):
        if self.errors >= 3:
            self.is_neutral = True

    def has_card_set(self):
        combos = itertools.combinations(self.cards, 3)
        for potential_set in combos:
            if potential_set[0].is_set_with(potential_set[1], potential_set[2]):
                return True
        return False

    def get_country_choice(self):
        pass

    def get_card_spend(self):
        pass

    def get_troop_deployment(self, game):
        pass

    def reinforcement_order(self):
        pass

    def get_attack_order(self):
        pass

    def send_game(self, game):
        pass

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, Player) and self.name == other.name



class Players(object):

    def __init__(self):
        self.players_list = []
        self.game_started = False

    def add_player(self, player):
        assert not self.game_started
        self.players_list.append(player)

    def start_game(self):
        assert 3 <= len(self.players_list) <= 6
        self.game_started = True
        random.shuffle(self.players_list)
        self.players_cycle = itertools.cycle(self.players_list)
        self.current_player = self.players_list[0]
        self.__generate_other_players()

    def __iter__(self):
        return (player for player in self.players_list)

    def __getitem__(self, key):
        return self.players_list[key]

    def __len__(self):
        return len(self.players_list)

    def __generate_other_players(self):
        self.other_players = [player for player in self.players_list if player is not self.current_player]

    def next(self):
        self.current_player = self.players_cycle.next()
        self.__generate_other_players()
        return self.current_player

    def restart(self):
        self.players_cycle = itertools.cycle(self.players_list)
        self.current_player = self.players_list[0]
        self.__generate_other_players()

    def choose_country(self, game):
        while not self.current_player.get_country_choice(game):
            self.broadcast_game(game)
        self.broadcast_game(game)

    def spend_cards(self, game):
        if self.current_player.has_card_set():
            while not self.current_player.get_card_spend(game):
               self.broadcast_game(game)
            self.broadcast_game(game)

    def force_cards_spend(self, game):
        assert len(self.current_player.cards) >= 5
        while not self.current_player.get_card_spend(game, force=True):
            self.broadcast_game(game)
        self.broadcast_game(game)

    def deploy_troops(self, game):
        while not self.current_player.get_troop_deployment(game):
            self.broadcast_game(game)
        self.broadcast_game(game)

    def attack(self, game):
        while not self.current_player.get_attack_order(game):
            self.broadcast_game(game)
        self.broadcast_game(game)

    def reinforce(self, game):
        while not self.current_player.get_reinforce_order(game):
            self.broadcast_game(game)
        self.broadcast_game(game)

    def broadcast_game(self, game):
        [player.broadcast_game(game) for player in self.other_players]


def import_board_data(json_url):
    board_file = open(json_url)
    board_json = json.load(board_file)
    board_file.close()
    board = Board()
    countries = {}
    cards = {}
    #go through the json and create the list of countries
    for continent_name in board_json:
        board.continents[continent_name] = Continent(continent_name,board_json[continent_name]["bonus"])
        for country_name in board_json[continent_name]["countries"]:
            countries[country_name] = Country(country_name, board_json[continent_name]["countries"][country_name]["border countries"])
            cards[country_name] = (Card(country_name, board_json[continent_name]["countries"][country_name]["card"]))
            board.continents[continent_name].countries[country_name] = countries[country_name]
    #loop through the country list and replace all of the border country strings with references to that country
    for country_name in countries:
        borders = [countries[name] for name in countries[country_name].border_countries]
        countries[country_name].border_countries = borders
    board.countries = countries
    #add the two wild cards
    cards['wild1'] = (Card("wild1", "wild"))
    cards['wild2'] = (Card("wild2", "wild"))
    #add cards to board
    board.cards = cards
    #return a tuple with the board and the cards
    return board
