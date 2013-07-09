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

    def get_country_choice(self, game):
        if self.if_neutral:
            country = random.choice([c for c in game.board.countries.values() if not c.owner])
            country.add_troops(self,1)
        else:
            self.avaliable_actions = ['choose_country']
            payload = {'risk': game.game_state_json(self)}
            try:
                r = requests.post(self.turn_url, data=payload, timeout=self.timeout)
                r = json.loads(r.json())
                assert r['action'] in self.avaliable_actions
                country = game.board.countries[r['data']]
                country.add_troops(self,1)
            except:
                self.errors += 1
                game.last_action = 'error %s' % self.error
                self.check_neutralized()
                self.get_country_choice(game)

        self.avaliable_actions = []
        game.last_aciton = "%s chose country %s" % (self,country)
