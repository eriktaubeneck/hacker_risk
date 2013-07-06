import json
import models


def generate_board():
    board_file = open('./board_graph.json')
    board_json = json.load(board_file)
    board_file.close()
    board = models.Board()
    countries = {}
    cards = {}
    for continent_name in board_json:
        board.continents[continent_name] = models.Continent(continent_name,
                                                            board_json[continent_name]["bonus"])
        for country_name in board_json[continent_name]["countries"]:
            countries[country_name] = models.Country(country_name,
                                                     board_json[continent_name]["countries"][country_name])
            cards.add(models.Card(country_name, countries[country_name]))
            board.continents[continent_name].countries[country_name] = countries[country_name]
    for country_name in countries:
        borders = [countries[name] for name in countries[country_name].border_countries]
        countries[country_name].border_countries = borders
    board.countries = countries
    return board, cards


if __name__ == '__main__':
    board = generate_board()
