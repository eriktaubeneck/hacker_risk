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

    def __init__(self, players_list):
        self.board, self.card_deck = generate_board()
        self.player_list = random.shuffle(list(player_list))
        self.card_deck = random.shuffle(list(card_deck))
        self.uid = uuid4()
        self.init_turn = 0
        self.init_turn = len(self.board.countries) + initial_troops[len(self.player_list)]
        self.turn = 0
        self.max_turns = 1000

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

        for _ in xrange(len(player_list) * initial_troops(len(player_list))):
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
            if(player.earned_card_this_turn and card_deck):
                player.earned_card_this_turn = False
                player.cards.add(card_deck.next())


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
        players_remaining = [p for p in players if (not p.is_eliminated) and (not p.is_neutral)]
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
