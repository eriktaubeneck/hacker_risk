import re
import models


def generate_board():
    countries_file = open('./countries_graph.txt')
    current_continent = None
    current_country = None
    board = models.Board()
    for line in countries_file:
        split_line = re.split("\s", line)
        if(split_line[0] != ''):  # we are on a continent
            current_continent = models.Continent(' '.join(split_line[:-2]), split_line[:-1])
            board.continents[current_continent.name] = current_continent
        else:
            if(split_line[0] == '' and split_line[1] != ''):  # we are on a country
                current_country = models.Country(' '.join(split_line[1:-2]))
                current_continent.countries[int(split_line[-2:-1][0])] = current_country
                board.countries[split_line[-2:-1][0]] = current_country
            else:  # we are defining the relations
                for c in split_line[3:-1]:
                    current_country.border_countries.append(c.replace(",", ""))
    new_countries = {}
    for c_id in board.countries:
        board.countries[c_id].border_countries = [board.countries[x] for x in board.countries[c_id].border_countries]
        new_countries[board.countries[c_id].name] = board.countries[c_id]
    board.countries = new_countries
    return board

if __name__ == '__main__':
    board = generate_board()
