from uuid import uuid4
import random
import math
import itertools
import models
import json

initial_troops = {3: 35,
                  4: 30,
                  5: 25,
                  6: 20}


class Game(object):

    def __init__(self, player_list):
        self.board, self.card_deck = self.import_board_graph('./board_graph.json')
        random.shuffle(list(player_list)) #     FYI
        self.player_list = player_list ##       random.shuffle() works in-place
        random.shuffle(list(self.card_deck)) #  and returns None
        self.uid = uuid4()
        self.init_turn = 0
        try:
            self.init_turn = len(self.board.countries) +\
                    initial_troops[len(self.player_list)]
        except KeyError:
            print("Invalid number of players")

        self.turn = 0
        self.max_turns = 1000
        self.card_sets_traded_in = 0

    def start_game(self):
        #assign countries to players
        self.init_deploy(self.player_list)
        self.play_game(self.player_list)

    def init_deploy(self):
        players = itertools.cycle(self.player_list)
        while {c for c in self.board.countries if not c.owner}:
            self.init_turn += 1
            player = players.next()
            player.choose_country(self.board)

        for _ in xrange(len(self.player_list) * \
                self.initial_troops(len(self.player_list))):

            self.init_turn += 1
            player = players.next()
            player.deploy_troop(self.board)

    def play_game(self):
        players = itertools.cycle(self.player_list)
        while not self.check_for_winner():
            self.turn += 1
            self.player = players.next()
            self.deployment_phase(self.player)
            player_done = False
            while not player_done:
                player_done = self.attacking_phase(self.player)
            self.reinforce(self.player)
            if(self.player.earned_card_this_turn and self.card_deck):
                self.player.earned_card_this_turn = False
                self.player.cards.add(self.card_deck.next())

    def deployment_phase(self, player):
        self.phase = 'deployment' 
        #card troops
        card_troops = player.use_cards(self.board)
        #base troops
        new_troops = max(math.ceil(len(player.countries)), 3)
        #continent troops
        continent_troops = sum({con.bonus for con in self.board.continents
                                if con.get_player_set == {player}})
        player.deploy_troops(self.board, card_troops + new_troops + continent_troops)

    def attacking_phase(self, player):
        self.phase = 'attacking'
        attacking_country, defending_country, attacking_troops = player.attack()
        if not attacking_country:
            return True
        assert attacking_country.owner == player
        country_invaded = attacking_country.attack(defending_country, attacking_troops)
        if country_invaded and not player.earned_card_this_turn:
            player.earned_card_this_turn = True
        if not defending_country.owner.countries:
            self.eliminate_player(player, defending_country.owner)
            if len(player.cards) >= 5:
                player.force_cards_spend()
        return False

    def check_for_winner(self):
        players_remaining = [p for p in self.players 
                             if (not p.is_eliminated) and (not p.is_neutral)]

        if len(players_remaining) == 1:
            return players_remaining[0]
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

    def get_troops_for_card_set(self, player, traded_cards):
        cards = list(traded_cards)
        assert len(cards) == 3
        if not cards[0].is_set_with(cards[1], cards[2]):
            return False
        for i in range(3):
            if cards[i].country in player.countries:
                cards[i].country.troops += 2
                break
        if(self.card_sets_traded_in < 6):
            self.card_sets_traded_in += 1
            return (self.card_sets_traded_in + 2) * 2
        else:
            self.card_sets_traded_in += 1
            return (self.card_sets_traded_in - 3) * 5

    def import_board_graph(self, json_url):
        board_file = open(json_url)
        board_json = json.load(board_file)
        board_file.close()
        board = models.Board()
        countries = {}
        cards = []
        #go through the json and create the list of countries
        for continent_name in board_json:
            board.continents[continent_name] = \
                    models.Continent(continent_name,
                                     board_json[continent_name]["bonus"])

            for country_name in board_json[continent_name]["countries"]:
                countries[country_name] = \
                        models.Country(country_name,
                                       board_json[continent_name]["countries"]\
                                                 [country_name]["border countries"])

                cards.append(models.Card(countries[country_name],
                    board_json[continent_name]["countries"][country_name]["card"]))

                board.continents[continent_name].countries[country_name]\
                        = countries[country_name]
        #loop through the country list and replace all 
        #of the border country strings with references to that country
        for country_name in countries:
            borders = [countries[name] 
                       for name in countries[country_name].border_countries]

            countries[country_name].border_countries = borders
        board.countries = countries
        #add the two wild cards
        cards.append(models.Card(None, "wild"))
        cards.append(models.Card(None, "wild"))
        #return a tuple with the board and the cards
        return board, cards
