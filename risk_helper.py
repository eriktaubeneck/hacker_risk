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

    def send_request(self, game):
        payload = {'risk': game.game_state_json(self)}
        r = requests.post(self.turn_url, data=payload, timeout=self.timeout)
        r = json.loads(r.json())
        assert r['action'] in self.avaliable_actions
        return r

    def got_exception(self, game):
        self.errors += 1
        game.last_action = 'error %s' % self.error
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
            self.got_exception(game)
            print e
            return False

        self.avaliable_actions = []
        game.last_aciton = "%s chose country %s" % (self,country)

    def get_troop_deployment(self, game):
        if self.is_neutral:
            game.last_action = "pass % is neutral"
            return True

        self.avaliable_actions = ['deploy_troops']
        try:
            r = self.send_requests(game)
            for country_name in r['data'].keys():
                country = game.board.countries[country_name]
                country.add_troops(self, countries[country])
            game.last_action = "%s deployed %s" % (self.name, r['data'])
            self.avaliable_actions = []
            return True

        except Exception as e:
            self.got_exception(game)
            print e
            return False

        self.avaliable_actions = []
