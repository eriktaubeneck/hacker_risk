from uuid import uuid4
import random
import math
import json
import models

initial_troops = {3: 35,
                  4: 30,
                  5: 25,
                  6: 20}


class Game(object):

    def __init__(self, players):
        self.board, self.card_deck = models.import_board_data('./board_graph.json')
        self.players = players
        random.shuffle(self.card_deck)
        self.uid = uuid4()
        self.init_turn = 0
        self.init_turn = len(self.board.countries) + initial_troops[len(self.players)]
        self.turn = 0
        self.max_turns = 1000
        self.card_sets_traded_in = 0
        self.winner = None
        self.last_action = ''

    def start_game(self):
        #assign countries to players
        self.players.start_game()
        self.init_deploy()
        self.play_game()

    def init_deploy(self):

        troops_to_deploy = initial_troops[len(self.players)]

        while {c for c in self.board.countries.values() if not c.owner}:
            self.players.next()
            self.init_turn += 1
            self.players.choose_country(self)
            troops_to_deploy -= 1

        for _ in xrange(len(self.players) * troops_to_deploy):
            self.players.next()
            self.init_turn += 1
            self.players.deploy_troops(self, 1)

    def play_game(self):
        self.players.restart()
        while not self.check_for_winner():
            self.turn += 1
            self.players.next()
            self.deployment_phase()
            player_done = False
            while not player_done:
                player_done = self.attacking_phase()
            self.reinforce()
            if(self.players.current_player.earned_card_this_turn and self.card_deck):
                self.players.current_player.earned_card_this_turn = False
                self.players.current_player.cards.add(self.card_deck.next())

    def deployment_phase(self):
        self.phase = 'deployment'

        self.players.current_player.troops_to_deploy += max(math.ceil(len(self.players.current_player.countries)), 3)
        self.players.current_player.troops_to_deploy += sum({con.bonus for con in self.board.continents
                                                             if con.get_player_set() == {self.players.current_player}})
        self.players.spend_cards(self)
        self.players.deploy_troops(self)

    def attacking_phase(self):
        self.phase = 'attacking'
        attacking_country, defending_country, attacking_troops, moving_troops = self.players.attack()
        if not attacking_country:
            return True
        assert attacking_country.owner == self.players.current_player
        country_invaded = attacking_country.attack(defending_country, attacking_troops, moving_troops)
        if country_invaded and not self.players.current_player.earned_card_this_turn:
            self.players.current_player.earned_card_this_turn = True
        if not defending_country.owner.countries:
            self.eliminate_player(self.players.current_player, defending_country.owner)
            if len(self.players.current_player.cards) >= 5:
                self.players.force_cards_spend(self)
        return False

    def reinforce(self):
        origin_country, destination_country, troops = self.players.reinforce(self)
        assert origin_country.owner == self.players.current_player
        assert destination_country.owner == self.players.current_player
        assert origin_country.troops - troops >= 1
        if not origin_country:
            return True
        destination_country.add_troops(self.players.current_player, troops)
        origin_country.troops -= troops

    def check_for_winner(self):
        players_remaining = {p for p in self.players_list if not p.is_eliminated}
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

    def get_troops_for_card_set(self, cards):
        assert len(cards) == 3
        for card in cards:
            assert card in self.players.current_player.cards
        assert cards[0].is_set_with(cards[1], cards[2])
        self.players.current_player.cards -= set(cards)
        for card in cards:
            if card.country in self.players.current_player.countries:
                card.country.troops += 2
                break
        if(self.card_sets_traded_in < 6):
            self.card_sets_traded_in += 1
            return (self.card_sets_traded_in-1 + 2) * 2
        else:
            self.card_sets_traded_in += 1
            return (self.card_sets_traded_in - 3) * 5

    def game_state_json(self, player): # player should be a Player object
        """
        Returns game state as JSON for sending to clients.
        Where g = Game(*args), 
        g.game_state_json(player)
        returns a JSON object of the entire game state as visible to player,
        where player is the requesting player
        """
        game_state = {'game':{},'you':{}}
        game_state['game']['continents'] = {}
        for key in self.board.continents:
            continent = self.board.continents[key]
            game_state['game']['continents'][key] = continent

        game_state['you'] = player
        return json.dumps(game_state, cls=GameEncoder)


class GameEncoder(json.JSONEncoder):
    """Special JSON encoder for our objects"""
    def default(self, obj):
        if isinstance(obj, models.Country):
            return { 'owner':obj.owner,
                    'troops':obj.troops
            }

        elif isinstance(obj, models.Player):
            return { 'is_eliminated':obj.is_eliminated,
                     'cards':list(obj.cards),
                     'earned_cards_this_turn':obj.earned_card_this_turn,
                     'countries':[ country.name for country in obj.countries ],
                     'troops_to_deploy':obj.troops_to_deploy,
                     'avaliable_actions':obj.avaliable_actions,
            }

        elif isinstance(obj, models.Continent):
            return {'countries': obj.countries, 'bonus':obj.bonus}

        elif isinstance(obj, models.Card):
            return { 'country':obj.country, 'value':obj.value }

        else: 
            return json.JSONEncoder.default(self, obj)
