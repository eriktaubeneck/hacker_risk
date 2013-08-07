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
        self.board = models.import_board_data()
        self.card_deck = self.board.cards.values()
        self.players = players
        random.shuffle(self.card_deck)
        self.uid = uuid4()
        self.init_turn = 0
        self.init_turn = len(self.board.countries) + initial_troops[len(self.players)]
        self.turn = 0
        self.max_turns = 1000
        self.broadcast_count = 0
        self.card_sets_traded_in = 0
        self.winner = None
        self.last_action = ''

    def start_game(self):
        #assign countries to players
        self.players.start_game()
        self.init_deploy()
        self.play_game()

    def init_deploy(self):

        print "started deployment"

        troops_to_deploy = initial_troops[len(self.players)]*len(self.players)

        while {c for c in self.board.countries.values() if not c.owner}:
            self.players.next()
            self.init_turn += 1
            self.players.choose_country(self)
            troops_to_deploy -= 1

        print "countries choosen"
        print {p.name:[c.name for c in p.countries] for p in self.players}

        for _ in xrange(troops_to_deploy):
            self.players.next()
            self.init_turn += 1
            self.players.current_player.troops_to_deploy = 1
            self.players.deploy_troops(self)

        print "initial troops deployed"

    def play_game(self):

        print "starting game"

        self.players.restart()
        while not self.check_for_winner():
            self.turn += 1
            print "starting turn %s - player %s's turn" % (self.turn, self.players.current_player.name)
            print {p.name:{'countries':len(p.countries),'total troops':sum([c.troops for c in p.countries])} for p in self.players}
            self.players.next()
            self.deployment_phase()
            self.players.attack(self)
            self.players.reinforce(self)
            if(self.players.current_player.earned_card_this_turn and self.card_deck):
                self.players.current_player.earned_card_this_turn = False
                self.players.current_player.cards.add(self.card_deck.pop())

    def deployment_phase(self):
        self.phase = 'deployment'

        self.players.current_player.troops_to_deploy += max(int(math.ceil(len(self.players.current_player.countries)/3.)), 3)
        self.players.current_player.troops_to_deploy += sum({con.bonus for con in self.board.continents.values()
                                                             if con.get_player_set() == {self.players.current_player}})
        self.players.spend_cards(self)
        self.players.deploy_troops(self)

    def attack(self, attacking_country, defending_country, attacking_troops, moving_troops):
        self.phase = 'attacking'
        assert attacking_country.owner == self.players.current_player
        defending_country_player = defending_country.owner
        country_invaded = attacking_country.attack(defending_country, attacking_troops, moving_troops)
        if country_invaded and not self.players.current_player.earned_card_this_turn:
            self.players.current_player.earned_card_this_turn = True
        if not defending_country_player.countries:
            self.eliminate_player(self.players.current_player, defending_country_player)
            if len(self.players.current_player.cards) >= 5:
                self.players.force_cards_spend(self)
        return country_invaded

    def reinforce(self, origin_country, destination_country, troops):
        assert origin_country.owner == self.players.current_player
        assert destination_country.owner == self.players.current_player
        assert origin_country.troops - troops >= 1
        if not origin_country:
            return True
        destination_country.add_troops(self.players.current_player, troops)
        origin_country.troops -= troops

    def check_for_winner(self):
        players_remaining = {p for p in self.players if not p.is_eliminated}
        neutral_players = {p for p in players_remaining if p.is_neutral}
        if len(players_remaining) == 1:
            self.winner = list(players_remaining)[0]
            print "Player %s DOMINATES!" % self.winner.name
            return True
        elif players_remaining == neutral_players:
            self.winner = None
            print "All players quit. DRAW"
            return True
        elif self.turn == self.max_turns:
            self.winner = None
            print "Reached 1000 turns. DRAW"
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
        for card in [c for c in cards if c.value != 'wild']:
            if self.board.countries[card.country_name] in self.players.current_player.countries:
                self.board.countries[card.country_name].troops += 2
                break
        if(self.card_sets_traded_in < 6):
            self.card_sets_traded_in += 1
            return (self.card_sets_traded_in-1 + 2) * 2
        else:
            self.card_sets_traded_in += 1
            return (self.card_sets_traded_in - 3) * 5

    def game_state_json(self, player):
        """
        Returns game state as JSON for sending to clients.
        Where g = Game(*args),
        g.game_state_json(player)
        returns a JSON object of the entire game state as visible to player,
        where player is the requesting player
        """
        game_state = {'game':{},'you':{}}
        game_state['game']['countries'] = {}
        for key in self.board.countries:
            country = self.board.countries[key]
            game_state['game']['countries'][key] = country
        game_state['game']['players'] = self.players
        game_state['you'] = player
        game_state['game']['cards_left'] = len(self.card_deck)
        game_state['game']['turn'] = self.turn
        game_state['game']['uid'] = str(self.uid)
        game_state['game']['last_action'] = self.last_action
        game_state['game']['broadcast_count'] = self.broadcast_count
        return json.dumps({"risk":game_state}, cls=GameEncoder)


class GameEncoder(json.JSONEncoder):
    """Special JSON encoder for our objects"""
    def default(self, obj):
        if isinstance(obj, models.Country):
            if obj.owner is None:
                return {'owner': 'none',
                        'troops': obj.troops,
                        }
            else:
                return {'owner': obj.owner.name,
                        'troops': obj.troops,
                        }

        elif isinstance(obj, models.Player):
            return {'name': obj.name,
                    'is_eliminated': obj.is_eliminated,
                    'cards': list(obj.cards),
                    'earned_cards_this_turn': obj.earned_card_this_turn,
                    'countries': [country.name for country in obj.countries],
                    'troops_to_deploy': obj.troops_to_deploy,
                    'available_actions': obj.available_actions,
                    }
        elif isinstance(obj, models.Players):
            return {p.name:{'is_eliminated': p.is_eliminated,
                            'cards': len(p.cards),
                            'is_neutral': p.is_neutral,
                            }
                    for p in obj.players_list}
        elif isinstance(obj, models.Continent):
            return {'countries': obj.countries, 'bonus': obj.bonus}

        elif isinstance(obj, models.Card):
            return {'country_name':obj.country_name, 'value': obj.value}

        else:
            return json.JSONEncoder.default(self, obj)
