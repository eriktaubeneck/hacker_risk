from risk.models import Player as BasePlayer, Players as BasePlayers
import requests

class Player(BasePlayer):

    def __init__(self, name, base_url):
        super(Player, self).__init__(name)
        self.base_url = base_url
        self.turn_url = self.base_url+"/turn"
        self.broadcast_url = self.base_url+"/get_board"
        
    def get_country_choice(game):
        self.avaliable_actions = ['choose_country']
        payload = {'risk': game.game_state_json(self)}
        r = requests.post(self.turn_url, data=payload)
