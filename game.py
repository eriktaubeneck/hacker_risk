from boardgen import generate_board
from uuid import uuid4
import random

class Game(object):

    def __init__(self, players_list):
        self.phases = ['place','attack','reinforce']
        self.board = generate_board()
        self.players_list = list(players_list)
        random.shuffle(self.players_list)
        self.uid = uuid4()

        #assign countries to players
        self.players = self.player_gen()
        for country in self.board.countries:
            self.players.next().countries.add(country)

        self.current_phase_index = 0
        self.players = self.player_gen() # reset players to start with p1
        self.current_player = self.players.next()

    def player_gen(self):
        index = 0
        while(True): 
            if index >= len(self.players_list):
                index = 0
            yield self.players_list[index]
            index += 1

    def finish_turn(self):
        self.current_player = self.players.next()
        self.current_phase_index = 0
        self.check_for_winner()
       
    def next_phase(self):
        self.current_phase_index += 1
        if self.current_phase_index >= 3:
            self.finish_turn()

    def check_for_winner(self):
        if len(self.players) == 1:
            return self.players[0]

