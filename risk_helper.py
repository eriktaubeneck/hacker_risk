from risk.models import Player as BasePlayer, Players as BasePlayers
import requests
import json
import random

class Player(BasePlayer):

    def __init__(self, name, base_url):
        super(Player, self).__init__(name)
        self.base_url = base_url
        self.turn_url = self.base_url+"/turn"
        self.broadcast_url = self.base_url+"/get_board"
        self.timeout = 30.
        r = requests.get(self.base_url+"/status", timeout=self.timeout)
        assert r.status_code == 200

    def send_request(self, game):
        payload = {'risk': game.game_state_json(self)}
        r = requests.post(self.turn_url, data=payload, timeout=self.timeout)
        r = json.loads(r.json())
        assert r['action'] in self.avaliable_actions
        return r

    def got_exception(self, game, e):
        self.errors += 1
        game.last_action = 'error %s' % self.errors
        self.avaliable_actions = []
        print e
        self.check_neutralized()

    def get_country_choice(self, game):
        if self.is_neutral:
            country = random.choice([c for c in game.board.countries.values() if not c.owner])
            country.add_troops(self,1)
            return True
        self.avaliable_actions = ['choose_country']
        try:
            r = self.send_request(game)
            country = game.board.countries[r['data']]
            country.add_troops(self,1)
            self.avaliable_actions = []
            game.last_aciton = "%s chose country %s" % (self,country)
            return True
        except Exception as e:
            self.got_exception(game,e)
            return False

    def get_card_spend(self, game, force=False):
        assert self.has_card_set()
        if self.is_neutral():
            game.last_action = "%s is neutral, spent no cards" % self.name
            return True
        if len(self.cards) >= 5:
            force = True
        self.avaliable_actions = ['spend_cards']
        if not force:
            self.avaliable_actions = ['pass']
        try:
            r = self.send_request(game)
            if r['action'] == 'spend_cards':
                cards = [game.card_deck[k] for k in r['data']]
                self.troops_to_deploy += game.get_troops_for_card_set(cards)
                game.last_action = "%s spent cards %s" % (self.name, r['data'])
                self.avaliable_actions = []
                return True
            elif r['action'] == 'pass':
                game.last_action = "%s spent no cards" % self.name
                self.avaliable_actions = []
                return True
            else:
                raise NameError('good job, you broke causality')
        except Exception as e:
            self.got_exception(game, e)
            return False

    def get_troop_deployment(self, game):
        if self.is_neutral:
            game.last_action = "pass % is neutral" % self.name
            return True

        self.avaliable_actions = ['deploy_troops']
        try:
            r = self.send_requests(game)
            assert sum(r['data'].values()) == self.troops_to_deploy
            self.troops_to_deploy = 0
            for country_name in r['data'].keys():
                country = game.board.countries[country_name]
                country.add_troops(self, countries[country])
            game.last_action = "%s deployed %s" % (self.name, r['data'])
            self.avaliable_actions = []
            return True

        except Exception as e:
            self.got_exception(game, e)
            return False

    def get_attack_order(self, game):
        if self.is_neutral:
            game.last_action = "pass % is neutral" % self.name
            return True
        self.avaliable_actions = ['attack', 'end_attack_phase']
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
            assert attacking_country.owner == self
            result = attacking_country.attack(defending_country,
                                              attacking_troops,
                                              moving_troops)
            if result:
                game.last_action = "%s defeated %s" % (attacking_country,
                                                       defending_country)
                self.avaliable_actions = []
                return False
            else:
                attacking_country_lost = (attacking_country_pre_attack_troops -
                                          attacking_country.troops)
                defending_country_lost = (defending_country_pre_attack_troops -
                                          defending_country.troops)
                game.last_action = "%s attacked %s. %s lost %s. %s lost %s." \
                % (attacking_country, defending_country,
                   attacking_country, attacking_country_lost,
                   defending_country, defending_coutnry_lost)
                self.avaliable_actions = []
                return False
        except:
            self.got_exception(game)
            print e
            self.avaliable_actions = []
            return False
