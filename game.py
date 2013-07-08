from boardgen import generate_board
from uuid import uuid4
import random
import math
import itertools

initial_troops = {3: 35,
                  4: 30,
                  5: 25,
                  6: 20}


class Game(object):

    def __init__(self, players):
        self.board, self.card_deck = self.import_board_graph('./board_graph.json')
        self.players = players
        self.card_deck = random.shuffle(list(card_deck))
        self.uid = uuid4()
        self.init_turn = 0
        self.init_turn = len(self.board.countries) + initial_troops[len(self.players)]
        self.turn = 0
        self.max_turns = 1000
        self.card_sets_traded_in = 0
        self.winner = None

    def start_game(self):
        #assign countries to players
        self.init_deploy()
        self.play_game()

    def init_deploy(self):

        troops_to_deploy = initial_troops(len(players))

        while {c for c in self.board.countries if not c.owner}:
            self.players.next()
            self.init_turn += 1
            self.players.choose_country(self)
            troops_to_deploy -= 1

        for _ in xrange(len(players) * troops_to_deploy):
            self.players.next()
            self.init_turn += 1
            self.players.deploy_troops(self, 1)

    def play_game(self):
        self.players.reset()
        while not self.check_for_winner():
            self.turn += 1
            self.players.next()
            self.deployment_phase()
            player_done = False
            while not player_done:
                player_done = self.attacking_phase()
            self.reinforce()
            if(self.players.current_player.earned_card_this_turn and card_deck):
                self.players.current_player.earned_card_this_turn = False
                self.players.current_player.cards.add(card_deck.next())

    def deployment_phase(self):
        self.phase = 'deployment'
        #card troops
        card_troops = self.players.use_cards(self)
        #base troops
        new_troops = max(math.ceil(len(self.players.current_player.countries)), 3)
        #continent troops
        continent_troops = sum({con.bonus for con in self.board.continents
                                if con.get_player_set == {self.players.current_player}})
        players.deploy_troops(self, card_troops + new_troops + continent_troops)

    def attacking_phase(self):
        self.phase = 'attacking'
        attacking_country, defending_country, attacking_troops = self.players.current_player.attack()
        if not attacking_country:
            return True
        assert attacking_country.owner == self.players.current_player
        country_invaded = attacking_country.attack(defending_country, attacking_troops)
        if country_invaded and not self.players.current_player.earned_card_this_turn:
            self.players.current_player.earned_card_this_turn = True
        if not defending_country.owner.countries:
            self.eliminate_player(self.players.current_player, defending_country.owner)
            if len(self.players.current_player.cards) >= 5:
                self.players.current_player.force_cards_spend()
        return False

    def check_for_winner(self):
        players_remaining = {p for p in players if not p.is_eliminated}
        neutral_players = {p for p in players_remaining if p.is_neutral}
        if len(players_remaining) == 1:
            self.winner = list(players_remaining)[0]
            return True
        elif players_remaining == neutral_players:
            self.winner = "Draw"
            return True
        else:
            return False

    def eliminate_player(self, eliminator, eliminated):
        assert eliminator is not None
        assert eliminated is not None
        assert eliminator.is_eliminated is False
        assert eliminated.is_eliminated is False
        assert eliminator.is_neutral is False
        assert len(eliminated.countries) is 0

        eliminator.cards = eliminator.cards.union(eliminated.cards)
        eliminated.cards = set()
        eliminated.is_eliminated = True

    def get_troops_for_card_set(self, traded_cards):
        cards = list(traded_cards)
        assert len(cards) == 3
        if not cards[0].is_set_with(cards[1], cards[2]):
            return False
        for i in range(3):
            if cards[i].country in self.players.current_player.countries:
                cards[i].country.troops += 2
                break
        if(self.card_sets_traded_in < 6):
            self.card_sets_traded_in += 1
            return (self.card_sets_traded_in + 2) * 2
        else:
            self.card_sets_traded_in += 1
            return (self.card_sets_traded_in - 3) * 5

    def import_board_graph(json_url):
        board_file = open(json_url)
        board_json = json.load(board_file)
        board_file.close()
        board = models.Board()
        countries = {}
        cards = []
        #go through the json and create the list of countries
        for continent_name in board_json:
            board.continents[continent_name] = models.Continent(continent_name,
                                                                board_json[continent_name]["bonus"])
            for country_name in board_json[continent_name]["countries"]:
                countries[country_name] = models.Country(country_name,
                                                         board_json[continent_name]["countries"][country_name]["border countries"])
                cards.append(models.Card(countries[country_name], board_json[continent_name]["countries"][country_name]["card"]))
                board.continents[continent_name].countries[country_name] = countries[country_name]
        #loop through the country list and replace all of the border country strings with references to that country
        for country_name in countries:
            borders = [countries[name] for name in countries[country_name].border_countries]
            countries[country_name].border_countries = borders
        board.countries = countries
        #add the two wild cards
        cards.append(models.Card(None, "wild"))
        cards.append(models.Card(None, "wild"))
        #return a tuple with the board and the cards
        return board, cards
