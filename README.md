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

```
max(ceiling([# OF COUNTRIES YOU CONTROL] / 3), 3) + [TROOPS BOUGHT WITH RISK CARDS] + [CONTINENT BONUSES]
```

Thus you will always receive at least 3 troops on every turn.

You may also gain 2 additional troops from trading in risk cards for a country you own, but since you do not get to control the placement of those units, they will simply be added to that country.

### Risk Cards

At the end of any turn in which you have captured at least one territory, you will earn one (and only one) risk card. You are trying to collect sets of 3 cards in any of the following combinations:

- 3 cards of the same design (Infantry, Cavalry, Artillery)
- 1 of each three designs
- Any two card plus a wild card

If you have collected a set of three risk cards, you may turn them in at the beginning of your next turn, or you may wait. However, if you have 5 or 6 cards at the beginning of your turn, you must trade in at least one set, and you may choose to turn in more than one if you have it.

## API

To write an AI for this competition is relatively straightforward - you provide an HTTP server which responds correctly to the following API calls, and then register the URL or IP of that server with the central AI game server.

### API Request

The server will make a POST request to your URL with the POST variable "risk". A typical request might look like:

```
{
	"game": {
		"continents": {
			"europe": {
				"bonus": 5,
				"countries": {
					"northern europe": {
						"owner": "Erty's Awesome AI",
						"troops": 13
					},
					[...]
				}
			},
			[...]
		}
	},
	"you": {
		"cards": [{"country": "argentina", "value": "soldier"}],
		"earned_cards_this_turn": false,
		"is_eliminated": false,
		"countries": ["northern europe", "venezuela", "western united states"],
		"troops_to_deploy": 0,
		"available_actions": ["attack", "end_turn", "reinforce"]
	}
}
```

Where [...] indicates data omitted for brevity.

###You

An API request made to your server will have a "you" section, which indicates data about your current state in the game.

#### cards

An array containing the Risk cards which you currently hold. If you have more than 5 of these at the beginning of your turn, or after you eliminate and enemy (and take their cards), you will be forced to spend these cards through the ```spend_cards``` action.

#### earned_cards_this_turn

Whether or not you have successfully conquered at least one country this turn, and you will recieve a new card at the end of your turn to be spent the next turn.

#### is_eliminated

Whether or not you have been removed from the game, due to either owning no countries, or failing to abide by the rules of the server.

#### countries

A list of the names of all of the countries you own. You can find out more details about these countries in the game->continents array

#### available_actions

A list of the actions which your server can take in its current state. The actions which can be in this list are listed below.

##### choose_country

This is an action taken at the beginning of the game, while there are still countries without owners. By choosing a country, you commit one troop to that country - more troops can be added later via the deploy_troops command.

Response:

```
{"action": "choose_country", "data": "<The name of a country which is not yet owned>"}
```

Example:

```
{"action": "choose_country", "data": "eastern united states"}
```

##### deploy_troops

Add troops to a country. In the "you" object, there is a parameter called ```troops_to_deploy``` which is the number of troops which you have available to deploy. If ```troops_to_deploy >0```, ```deploy_troops``` will be the only action available. You will not have this action available if you have no troops to deploy. You must deploy your troops before the ```attack``` action will become available.

 - You can only deploy to a country you are the owner of.
 - You can only deploy the number of troops you have in troops_to_deploy (no more no less).

Response:

```
{"action": "deploy_troops", "data": {"<country 0>": <number of troops for country 0>, "country 1": <number of troops for country 1> ...}}
```

Example:

```
{"action": "deploy_troops", "data": {"eastern united states": 3, "western united states": 2}}
```

##### use_cards

Trade in a set of cards for units. You can do this at the beginning of your turn or (after you eliminate a player and you now have >= 5 cards).

 - You must submit a valid set of cards (3 of the same, or 1 of each)
 - You must hold each of the cards you wish to submit
 - Cards are represented by their country name
 - Wild cards are represented by the string "wild"
 - The cards should be sent as a list. If you own any of the countries on the cards, only the first one in the list will be credited 2 extra units.
 - This option may be available even if you don't have a valid set of cards

Response:

```
{"action": "use_cards", "data": [<card 1>, <card 2>, <card 3>]}
```

Example:

```
{"action": "use_cards", "data": ["argentina", "china", "iceland"]}
```

##### attack

Attack a country adjacent to one of your countries. Specify an origin country,  destination country, number of troops to attack with (1, 2, or 3), and a number of troops to move if you win the engagement.

 - There is no way to lose troops and conquer a country in the same attack round
 - The opponent will always defend with as many troops as they can (1 or 2)
 - The attacking and defending countries must be adjacent
 - You must own the attacking country, and not the defending country
 - You must leave at least one unit in the attacking country when you invade the defending country
 - This command may be available even if you have no legal attacks

Response:

```
{"action": "attack", "data": {"attacking_country": "<attacking country name>", "defending_country": "<defending country name>", "attacking_troops": <number of attacking troops>, "moving_troops": <number of troops to move into the country if you win>}}
```

Example:

```
{"action": "attack", "data": {"attacking_country": "western united states", "defending_country": "eastern united states", "attacking_troops": 3, "moving_troops": 15}}
```

##### reinforce

This command allows you to move troops from one of your countries to an adjacent country, once. Performing this action will end your turn.

 - You must leave at least one unit in the origin country
 - You must move at least one unit to the destination country
 - You must have the number of troops in the origin country that you wish to move
 - You must own the origin and destination countries

Response:

```
{"action": "reinforce", "data": {"origin_country": "<origin country name>", "destination_country": "<destination country name>", "moving_troops": <number of troops to move>}}
```

Example:

```
{"action": "reinforce", "data": {"origin_country": "greenland", "destination_country": "iceland", "moving_troops": 7}}
```

##### end_turn

If you wish to end your turn without reinforcing, you may perform the ```end_turn``` action. This action takes no extra data parameters.

Response:

```
{"action": "end_turn"}
```

Example:

```
{"action": "end_turn"}
```

### Game Flow

The game starts with all players choosing countries one at a time, using the ```choose_country``` command. After all countries have been chosen, players will place troops using the ```deploy_troops``` command, one troop at a time.

At the beginning of a player's turn, if the player has more than three cards, the ```use_cards``` and ```deploy_troops``` options will be available. If you have more than 5 cards, the ```use_cards``` option will be the only one available, and after performing that action, ```deploy_troops``` will become available.

During the main phase of a turn, the actions available are ```attack```, ```reinforce```, and ```end_turn```. A player may attack as many times as they want during a turn. Calling ```reinforce``` or ```end_turn``` will end the player's turn and move on to the next.