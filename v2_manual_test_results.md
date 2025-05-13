# Example workflow
A game developer is adding items for a spring update that introduces new seasonal foods and enchantments to the game.

- "As a game designer, I want to have a database of all foods, so that I can add new foods that are unique from current food offerings."
- “As a game developer, I want to implement different rarities of items, so that players are motivated to explore other parts of the game and have interactions with other players.”

1. First, the developer must check that the special spring cherry blossom cake wasn’t already added to the global items database:

GET /items/9002


	The food wasn’t added yet, so the developer will receive a helpful message informing them that the item with the item_id of 9002 isn’t in the database.
2. Since the food item wasn’t added yet, the developer then adds the new special food for a spring event:
 
POST /items
[
    {
      “item_id”: “9002”,
      “name”: “cherry blossom cake”,
      “item_type”: “food”, /* weapon, food, clothing */
      “rarity”: “legendary”
    }
]
3. Then, the developer adds a new enchantment to accompany the spring food being added:


POST /enchantments
[
    {
      “enchantment_id”: “3522”,
      “name”: “Golden Grub”
      "effect_description": "Eating this food drops a small amount of gold coins on the ground around you."
    }
]
After this, players will be able to find the cherry blossom cake in loot drops, and the Golden Grub enchantment will be available for use.

# Testing results (Repeated for each step of the workflow)
1.
curl -X 'GET' \
  'http://item-management-api-dl6u.onrender.com/items/6' \
  -H 'accept: application/json' \
  -H 'access_token: brat'
Response:
HTTP/1.1 404 Not Found
{
  "detail": "Item with ID 9999 not found in the database."
}


2.
curl -X 'POST' \
  'http://item-management-api-dl6u.onrender.com/items' \
  -H 'accept: application/json' \
  -H 'access_token: brat' \
  -d '{
    "item_id": 9002,
    "name": "cherry blossom cake",
    "item_type": "food",
    "rarity": "legendary"
}'
Response:
HTTP/1.1 201 Created


3.
curl -X 'POST' \
  'http://item-management-api-dl6u.onrender.com/enchantments \
  -H 'accept: application/json' \
  -H 'access_token: brat' \
  -d '{
  "enchantment_id": 3522,
  "name": "Golden Grub",
  "effect_description": "Eating this food drops a small amount of gold coins on the ground around you."
  }'
Response:
HTTP/1.1 201 Created


# Example workflow
A multiplayer game moderator has received complaints about a legendary sword and corresponding enchantment being bugged and overpowered. To ensure gameplay fairness, the moderator will remove the legendary sword and enchantment from the game.
"As a multiplayer game moderator, I want to reset or remove specific items from the game via the backend if they're bugged, so that I can maintain fair play."

1. First, the developer gets the sword’s corresponding info to check if any of the metadata is responsible for the bug:
[
   {
      “item_id”: 1021,
      “name”: “Glowing Longsword”,
      “item_type”: “weapon”,
      “rarity”: “legendary”
   }
]
2. The metadata is correct, so the developer removes the overpowered legendary sword:

DELETE /items/1021

3. The developer also removes the overpowered enchantment:

DELETE /enchantments/4552

After this, the bugged sword and enchantment will no longer be in loot drops, and it will be removed from all player inventories as well.

# Testing results (Repeated for each step of the workflow)
1.
curl -X 'GET' \
  'http://127.0.0.1:3000/items/1021' \
  -H 'accept: application/json' \
  -H 'access_token: brat'
Response:
HTTP/1.1 202
{
  "item_id": 1021,
  "name": "Glowing Longsword",
  "item_type": "weapon",
  "rarity": "legendary"
}


2.
curl -X 'DELETE' \
  http://localhost:8000/items/1021 \
  -H 'access_token: brat'
Response:
HTTP/1.1 204 No Content


3.
curl -X 'DELETE' \
  http://localhost:8000/enchantments/4552 \
  -H 'access_token: brat'
Response:
HTTP/1.1 204 No Content
