API Specification and Example Flows
Manage player inventories
1.1. Get a player’s inventory - /players/{player_id}/inventory (GET)
Response: 
[
    {
        “item_id”: “integer”,
        “name”: “string”,
        “item_type”: “string”, /* weapon, food, clothing */
        “rarity”: “string”, 
        “quantity”: “integer”,
        “enchantments”: [
      	 {
        	      "enchantment_id": "integer",
       	      "name": "string"
      	 }
         ]
    }
]
1.2. Add item to a player - /players/{player_id}/inventory (POST)
Request:
[
    {
        “item_id”: “integer”,
        “quantity”: “integer”, 
    }
]
1.3. Remove item from a player - /players/{player_id}/inventory (DELETE)
Request:
[
    {
       “quantity”: “integer”
     }
]
Enchant items
2.1. Enchant a player’s item - /players/{player_id}/inventory/{item_id}/enchant (POST)
Request:
[
    {
       “enchantment_id”: “integer”
     }
]
Manage global items
3.1. Create new global item - /items (POST)
Request:
[
    {
      “item_id”: “integer”,
      “name”: “string”,
      “item_type”: “string”, /* weapon, food, clothing */
      “rarity”: “string”,
    }
]
3.2. Remove global item - /items/{item_id} (DELETE)
3.3. Get item info - /items/{item_id} (GET)
Response:
[
   {
      “item_id”: “integer”,
      “name”: “string”,
      “item_type”: “string”,
      “rarity”: “string”
   }
]
3.4. Create new global enchantment - /enchantments (POST)
Request:
[
    {
      “enchantment_id”: “integer”,
      “name”: “string”,
      “effect_description”: “string”
    }
]
3.5. Remove global enchantment - /enchantments/{enchantment_id} (DELETE)

