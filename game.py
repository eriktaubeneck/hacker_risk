from boardgen import generate_board
from uuid import uuid4
import random
import math
import itertools

PHASE_DEPLOY = 0
PHASE_ATTACK = 1


class Game(object):

    def __init__(self, players_list):
        self.phases = ['place', 'attack', 'reinforce']
        self.board = generate_board()
        self.player_list = random.shuffle(list(player_list))
        self.uid = uuid4()

    def start_game(self):
        #assign countries to players
        self.init_deploy(player_list)

        self.current_phase_index = PHASE_DEPLOY
        self.players = self.player_gen()  # reset players to start with p1
        self.current_player = self.players.next()

    def init_deploy(self):
        players = itertools.cycle(self.player_list)
        while {c for c in self.board.countries if not c.owner}:
            player = players.next()
            player.choose_country(self.board)

        initial_troops = {3: 35,
                          4: 30,
                          5: 25,
                          6: 20}

        for _ in xrange(len(player_list) * initial_troops(len(player_list))):
            player = players.next()
            player.deploy_troop(self.board)

    def play_game(self):
        players = itertools.cycle(self.player_list)
        while not self.check_for_winner():
            player = players.next()
            self.deployment_phase(player)
            player_done = False
            while not player_done:
                player_done = self.attacking_phase(player)
            self.reinforce(player)

    def deployment_phase(self, player):
        #card troops
        card_troops = player.use_cards(self.board)
        #base troops
        new_troops = max(math.ceil(len(player.countries)), 3)
        #continent troops
        continent_troops = sum({con.bonus for con in self.board.continents
                                if con.get_player_set == {player}})
        player.deploy_troops(self.board, card_troops + new_troops + continent_troops)

    def attacking_phase(self, player):
        attacking_country, defending_country, attacking_troops = player.attack()
        if not attacking_country:
            return True
        assert attacking_country.owner == player
        attacking_country.attack(defending_country, attacking_troops)
        if not defending_country.owner.countries:
            self.eliminate_player(player, defending_country.owner)
            if len(player.cards) >= 5:
                self.force_card_spend(player)
        return False

    def finish_turn(self):
        self.current_player = self.players.next()
        self.current_phase_index = PHASE_DEPLOY
        self.check_for_winner()

    def next_phase(self):
        self.current_phase_index += 1
        if self.current_phase_index > PHASE_ATTACK:
            self.finish_turn()

    def check_for_winner(self):
        players_remaining = [p for p in players if not p.is_neutral]
        if len(players_remaining) == 1:
            return players_remaining[0]
        else:
            return False

    def remove_player(self, eliminator, eliminated):
        assert eliminator is not None
        assert eliminated is not None
        assert eliminator.is_neutral is False
        assert len(eliminated.countries) is 0

        #transfer cards
        eliminator.cards += eliminated.cards
        eliminated.cards = set()
        #if 5 or more cards, they must be spent now
        while(len(eliminator.cards) >= 5):
            pass
            #TODO force cards to be spent
        #make the eliminated player is_neutral
        eliminated.is_neutral = True
