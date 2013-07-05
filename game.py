from boardgen import generate_board
from uuid import uuid4
import random
import itertools

class Game(object):

    def __init__(self, players_list):
        self.phases = ['place','attack','reinforce']
        self.board = generate_board()
        self.player_list = random.shuffle(list(player_list))
        self.uid = uuid4()


    def start_game(self):
        #assign countries to players
        self.init_deploy(player_list)
        

        self.current_phase_index = 0
        self.players = self.player_gen() # reset players to start with p1
        self.current_player = self.players.next()


    def init_deploy(self,player_list):
        players = itertools.cycle(self.player_list)
        while {c for c in self.board.countries if not c.owner}:
            player = players.next()
            player.choose_country(self.board)

        initial_troops = {3:35,
                          4:30,
                          5,25,
                          6,20}

        for _ in xrange(len(player_list) * initial_troops(len(player_list))):
            player = players.next()
            player.deploy_troop(self.board)
    

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

