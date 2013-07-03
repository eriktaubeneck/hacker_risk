# Hacker Risk

Based on <a href="http://www.hasbro.com/common/instruct/risk.pdf">the official Hasbro rules</a> - refer to these for any disputes.

## The Game Pieces

### Continents and Countries

The game board is a graph of 6 continents divided into 42 countries. Each continent contains from 4 to 12 countries.

The country names and graph data are available in the board_graph.json file.

### Armies

Armies are simply represented by an integer value, as part of the data for a country.

### Cards

There are 42 cards, marked with a territory and an infantry, cavalry, or artillery. There are two wild cards marked with all three pictures, but no territory.

## Object of the Game

To conquer the world by occupying every country, thus eliminating all your opponents.

## Setup

### Initial Army Placement
The number of troops that each player will need:

	- 3 Players: 35 Troops Each
	- 4 Players: 30 Troops Each
	- 5 Players: 25 Troops Each
	- 6 Players: 20 Troops Each

The order of play will be selected randomly by the server. Each player will take turns placing a troop into an empty country on the board. Once all countries have been taken, players continue placing troops on countries that they own, until they have run out of troops to place.

## Playing

Each turn consists of three steps, in this order:
1. Place new troops
2. Attack (optional)
3. Fortify one country

### Placing new troops

At the beginning of your turn, you will be able to trade in any risk cards (explained later). The number of troops you may place is then:

    max(ceiling([# OF COUNTRIES YOU CONTROL] / 3), 3) + [TROOPS BOUGHT WITH RISK CARDS] + [CONTINENT BONUSES]

Thus you will always receive at least 3 troops on every turn.

You may also gain 2 additional troops from trading in risk cards for a country you own, but since you do not get to control the placement of those units, they will simply be added to that country.

### Risk Cards

At the end of any turn in which you have captured at least one territory, you will earn one (and only one) risk card. You are trying to collect sets of 3 cards in any of the following combinations:

- 3 cards of the same design (Infantry, Cavalry, Artillery)
- 1 of each three designs
- Any two card plus a wild card

If you have collected a set of three risk cards, you may turn them in at the beginning of your next turn, or you may wait. However, if you have 5 or 6 cards at the beginning of your turn, you must trade in at least one set, and you may choose to turn in more than one if you have it.