from risk.models import Player as BasePlayer, Players as BasePlayers
import requests
import json
import random

class Player(BasePlayer):

    def __init__(self, name, base_url):
        super(Player, self).__init__(name)
        self.base_url = base_url
        self.turn_url = self.base_url+"/turn"
        self.broadcast_url = self.base_url+"/not_turn"
        self.timeout = 30.
        r = requests.get(self.base_url+"/status", timeout=self.timeout)
        assert r.status_code == 200

    def send_request(self, game):
        payload = {'risk': game.game_state_json(self)}
        r = requests.post(self.turn_url, data=payload, timeout=self.timeout)
        r = r.json()
        assert r['action'] in self.available_actions
        return r

    def got_exception(self, game, e):
        self.errors += 1
        game.last_action = 'error %s' % self.errors
        self.available_actions = []
        raise e
        self.check_neutralized()

    def get_country_choice(self, game):
        if self.is_neutral:
            country = random.choice([c for c in game.board.countries.values() if not c.owner])
            country.add_troops(self,1)
            return True
        self.available_actions = ['choose_country']
        try:
            r = self.send_request(game)
            country = game.board.countries[r['data']]
            country.add_troops(self,1)
            self.available_actions = []
            game.last_action = "%s chose country %s" % (self,country)
            return True
        except Exception as e:
            self.got_exception(game,e)
            return False

    def get_card_spend(self, game, force=False):
        assert self.has_card_set()
        if self.is_neutral:
            game.last_action = "%s is neutral, spent no cards" % self.name
            return True
        if len(self.cards) >= 5:
            force = True
        self.available_actions = ['spend_cards']
        if not force:
            self.available_actions.append('pass')
        try:
            r = self.send_request(game)
            if r['action'] == 'spend_cards':
                cards = [game.board.cards[k] for k in r['data']]
                self.troops_to_deploy += game.get_troops_for_card_set(cards)
                game.last_action = "%s spent cards %s" % (self.name, r['data'])
                self.available_actions = []
                return True
            elif r['action'] == 'pass':
                game.last_action = "%s spent no cards" % self.name
                self.available_actions = []
                return True
            else:
                raise NameError('good job, you broke causality')
        except Exception as e:
            self.got_exception(game, e)
            return False

    def get_troop_deployment(self, game):
        if self.is_neutral:
            game.last_action = "pass %s is neutral" % self.name
            return True

        self.available_actions = ['deploy_troops']
        try:
            r = self.send_request(game)
            assert sum(r['data'].values()) == self.troops_to_deploy
            self.troops_to_deploy = 0
            for country_name in r['data'].keys():
                country = game.board.countries[country_name]
                country.add_troops(self, r['data'][country_name])
            game.last_action = "%s deployed %s" % (self.name, r['data'])
            self.available_actions = []
            return True

        except Exception as e:
            self.got_exception(game, e)
            return False

    def get_attack_order(self, game):
        if self.is_neutral:
            game.last_action = "pass %s is neutral" % self.name
            return True
        self.available_actions = ['attack', 'end_attack_phase']
        try:
            r = self.send_request(game)
            if r['action'] == 'end_attack_phase':
                return True
            attacking_country = game.board.countries[r['data']['attacking_country']]
            defending_country = game.board.countries[r['data']['defending_country']]
            attacking_country_pre_attack_troops = attacking_country.troops
            defending_country_pre_attack_troops = defending_country.troops
            attacking_troops = r['data']['attacking_troops']
            moving_troops = r['data']['moving_troops']
            result = game.attack(attacking_country,
                                 defending_country,
                                 attacking_troops,
                                 moving_troops)
            if result:
                game.last_action = "%s defeated %s" % (attacking_country,
                                                       defending_country)
                self.available_actions = []
                return False
            else:
                attacking_country_lost = (attacking_country_pre_attack_troops -
                                          attacking_country.troops)
                defending_country_lost = (defending_country_pre_attack_troops -
                                          defending_country.troops)
                game.last_action = "%s attacked %s. %s lost %s. %s lost %s." \
                % (attacking_country, defending_country,
                   attacking_country, attacking_country_lost,
                   defending_country, defending_country_lost)
                self.available_actions = []
                return False
        except Exception as e:
            self.got_exception(game, e)
            return False

    def get_reinforce_order(self, game):
        if self.is_neutral:
            game.last_action = "pass %s is neutral" % self.name
            return True
        self.available_actions = ['reinforce', 'end_turn']
        try:
            r = self.send_request(game)
            if r['action'] == 'end_turn':
                return True
            origin_country = game.board.countries[r['data']['origin_country']]
            destination_country = game.board.countries[r['data']['destination_country']]
            moving_troops = r['data']['moving_troops']
            game.reinforce(origin_country, destination_country, moving_troops)
            game.last_action = "%s reinforced %s with %s troops" % (origin_country,
                                                                    destination_country,
                                                                    moving_troops)
            self.available_actions = []
            return True
        except Exception as e:
            self.got_exception(game, e)
            return False

    def broadcast_game(self, game):
        payload = {'risk': game.game_state_json(self)}
        try:
            r = requests.post(self.broadcast_url, data=payload, timeout=0.1)
        except requests.exceptions.Timeout:
            pass
