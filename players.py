import itertools
import random


class Players(object):

    def __init__(self, players_list):
        self.players_list = random.shuffle(players_list)
        self.players_cycle = itertools.cycle(players_list)
        self.current_player = self.players_list[0]
        self.__generate_other_players()

    def __iter__(self):
        return self.players_list

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
        pass

    def deploy_troops(self, game, number_of_troops):
        pass

    def use_cards(self, game):
        pass