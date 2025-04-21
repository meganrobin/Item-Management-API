Flow 1: Crafting and Enchanting a Weapon
Shows how a player checks their inventory, crafts an epic bow, adds an enchantment.

"As a crafting game developer, I want to check which ingredients a player has in their inventory, so that I can process item creation and deduct resources."
"As a player, I want to add enchantments to my weapons, so that there is more variability in the game and allow for more creativity."

In this scenario, player Megan wants to add a bow and then enchant it for an upcoming raid.

First, Megan checks their inventory to see what materials she has.

GET /players/megan783/inventory
[
    {
        “item_id”: “7863”,
        “name”: “Wooden sword”,
        “item_type”: “weapon”, /* weapon, food, clothing */
        “rarity”: “common”, 
        “quantity”: “1”
        “enchantments”:   []
    }
]
Megan removes the required materials from her inventory

DELETE /players/megan783/inventory/7863

[
    {
       “quantity”: “1”
     }
]
      3.  Now Megan wants to add the newly crafted enchanted bow to her inventory 

POST /players/megan783/inventory/

[
    {
        “item_id”: “3021”,
        “quantity”: “1”, 
    }
]
4. Now Megan wants to add an enchantment to the bow

POST /players/megan783/inventory/3021/enchant

[
    {
       “enchantment_id”: “1”
     }
]

After this flow, Megan has successfully equipped a new bow and added an enchantment to it.

Flow 2: Game developer managing global items and enchantments
A game developer is adding items for a spring update that introduces new seasonal foods and enchantments to the game. 

"As a game designer, I want to have a database of all foods, so that I can add new foods that are unique from current food offerings."
“As a game developer, I want to implement different rarities of items, so that players are motivated to explore other parts of the game and have interactions with other players.”

First, the developer must check that the special spring cherry blossom cake wasn’t already added to the global items database:

GET /items/9002

	The food wasn’t added yet, so the developer will receive a helpful message informing them that the item with the item_id of 9002 isn’t in the database.
Since the food item wasn’t added yet, the developer then adds the new special food for a spring event:
 
POST /items
[
    {
      “item_id”: “9002”,
      “name”: “cherry blossom cake”,
      “item_type”: “food”, /* weapon, food, clothing */
      “rarity”: “legendary”
    }
]
Then, the developer adds a new enchantment to accompany the spring food being added:

POST /enchantments
[
    {
      “enchantment_id”: “3522”,
      “name”: “Golden Grub”
      "effect_description": "Eating this food drops a small amount of gold coins on the ground around you."
    }
]

After this, players will be able to find the cherry blossom cake in loot drops, and the Golden Grub enchantment will be available for use.

Flow 3: Game moderator removing bugged items
A multiplayer game moderator has received complaints about a legendary sword and corresponding enchantment being bugged and overpowered. To ensure gameplay fairness, the moderator will remove the legendary sword and enchantment from the game.
"As a multiplayer game moderator, I want to reset or remove specific items from the game via the backend if they're bugged, so that I can maintain fair play."

First, the developer gets the sword’s corresponding info to check if any of the metadata is responsible for the bug:
[
   {
      “item_id”: 1021,
      “name”: “Glowing Longsword”,
      “item_type”: “weapon”,
      “rarity”: “legendary”
   }
]
The metadata is correct, so the developer removes the overpowered legendary sword:

DELETE /items/1021

The developer also removes the overpowered enchantment:

DELETE /enchantments/4552

After this, the bugged sword and enchantment will no longer be in loot drops, and it will be removed from all player inventories as well.
