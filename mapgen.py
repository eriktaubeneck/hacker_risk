import re
import models

def generateMap():
    countries_file = open('./countries_graph.txt')
    current_continent = None
    current_country = None
    themap = models.Map()
    for line in countries_file:
        split_line = re.split("\s", line)
        if(split_line[0] != ''): # we are on a continent
            current_continent = models.Continent(' '.join(split_line[:-2]), split_line[:-1])
            themap.continents[current_continent.name] = current_continent
        else:
            if(split_line[0] == '' and split_line[1] != ''): # we are on a country
                current_country = models.Country(' '.join(split_line[1:-2]))
                current_continent.countries[int(split_line[-2:-1][0])] = current_country
                themap.countries[int(split_line[-2:-1][0])] = current_country
            else: #we are defining the relations
                for c in split_line[3:-1]:
                    current_country.border_countries.add(c.replace(",",""))
    return themap

if __name__ == '__main__':
    print(generateMap())
