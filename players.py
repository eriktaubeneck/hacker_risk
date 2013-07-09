import itertools
import random


class Players(object):

    def __init__(self, players_list):
        random.shuffle(players_list)
        self.players_list=players_list
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
        self.current_player.get_country_choice(game)
        self.broadcast_game(game)

    def deploy_troops(self, game):
        self.current_player.get_troop_deployment(game)
        self.broadcast_game(game)

    def use_cards(self, game):
        self.current_player.get_card_spend(game)
        self.broadcast_game(game)

    def reinforce(self, game):
        self.get_reinforcement_order(game)
        self.broadcast_game(game)

    def broadcast_game(self, game):
        [player.send_game(game) for player in self.other_players]
