# Example workflow 1
A player named Megan wants to trade her common wooden sword for an epic bow, and then add an enchantment to her new bow for an upcoming raid.

- "As a crafting game developer, I want to check which ingredients a player has in their inventory, so that I can process item creation and deduct resources."
- "As a player, I want to add enchantments to my weapons, so that there is more variability in the game and allow for more creativity."

1. First, Megan checks her inventory to make sure she still has the wooden sword:

GET /players/1/inventory
[
  {
    "item_id": 4,
    "name": "wooden sword",
    "item_type": "weapon",
    "rarity": "common",
    "quantity": 1,
    "enchantments": []
  }
]

2. The sword is in Megan's inventory, so she removes the sword to give to the trader:

PATCH /players/1/inventory/4
[
  {
    "message": "Removed all 1 'wooden sword' from player 1's inventory",
    "item_id": 4,
    "quantity_removed": 1,
    "remaining": 0
  }
]

3. Megan adds the newly traded bow to her inventory:

POST /players/megan783/inventory/
[
  {
    "message": "Added 1 'emerald bow' to player 1's inventory",
    "item_id": 5,
    "name": "emerald bow",
    "quantity_added": 1,
    "total_quantity": 1
  }
]

4. Finally, Megan adds an enchantment to the bow:

POST /players/1/inventory/5/enchant
[
  {
    "message": "Successfully applied enchantment 'Ice Splinter' to 'emerald bow'",
    "item_id": 5,
    "item_name": "emerald bow",
    "enchantment_id": 1,
    "enchantment_name": "Ice Splinter"
  }
]

After this flow, Megan has successfully traded her wooden sword for a new epic bow and added an enchantment to it.

# Testing results (Repeated for each step of the workflow)
1. 

curl -X 'GET' \
  'http://127.0.0.1:3000/players/1/inventory' \
  -H 'accept: application/json' \
  -H 'access_token: brat'
Response:
{
  "items": [
    {
      "item_id": 4,
      "name": "wooden sword",
      "item_type": "weapon",
      "rarity": "common",
      "quantity": 1,
      "enchantments": []
    }
  ],
  "message": "Player 1 has 1 item(s) in their inventory."
}

2. 

curl -X 'PATCH' \
  'http://127.0.0.1:3000/players/1/inventory/4' \
  -H 'accept: application/json' \
  -H 'access_token: brat' \
  -H 'Content-Type: application/json' \
  -d '{
  "quantity": 1
}'
Response:
200 OK

3. 

curl -X 'POST' \
  'http://127.0.0.1:3000/players/1/inventory' \
  -H 'accept: application/json' \
  -H 'access_token: brat' \
  -H 'Content-Type: application/json' \
  -d '{
  "item_id": 5,
  "quantity": 1
}'
Response:
201	Created
{
  "message": "Added 1 'emerald bow' to player 1's inventory",
  "item_id": 5,
  "name": "emerald bow",
  "quantity_added": 1,
  "total_quantity": 1
}

4. 

curl -X 'POST' \
  'http://127.0.0.1:3000/players/1/inventory/5/enchant' \
  -H 'accept: application/json' \
  -H 'access_token: brat' \
  -H 'Content-Type: application/json' \
  -d '{
  "enchantment_id": 1
}'
Response:
201 Created
{
  "message": "Successfully applied enchantment 'Ice Splinter' to 'emerald bow'",
  "item_id": 5,
  "item_name": "emerald bow",
  "enchantment_id": 1,
  "enchantment_name": "Ice Splinter"
}