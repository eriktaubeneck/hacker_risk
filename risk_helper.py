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
                self.deployment_troops += game.get_troops_for_card_set(cards)
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
            self.got_exception(game)
            print e
            return False

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
