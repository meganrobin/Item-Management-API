# Example workflow
Flow 1: Crafting and Enchanting a Weapon
Shows how a player checks their inventory, crafts an epic bow, adds an enchantment.

"As a crafting game developer, I want to check which ingredients a player has in their inventory, so that I can process item creation and deduct resources."
"As a player, I want to add enchantments to my weapons, so that there is more variability in the game and allow for more creativity."

In this scenario, player Megan wants to add a bow and then enchant it for an upcoming raid.

1. First, Megan checks her inventory to see what materials she has:

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
2. Megan removes the required materials from her inventory:

DELETE /players/megan783/inventory/7863

[
    {
       “quantity”: “1”
     }
]
3. Now Megan wants to add the newly crafted enchanted bow to her inventory:

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

# Testing results (Repeated for each step of the workflow)
1. 
curl -X 'GET' \
  'https://item-management-api-dl6u.onrender.com/players/783/inventory' \
  -H 'accept: application/json'
Response:
[
    {
        “item_id”: “7863”,
        “name”: “Wooden sword”,
        “rarity”: “common”, 
        “quantity”: 1,
        “enchantments”: []
    }
]

2. 
curl -X 'DELETE' \
  'https://item-management-api-dl6u.onrender.com/players/783/inventory/7863' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
  "quantity": 1
}'
Response:
204	Successful Response

3. 
curl -X 'POST' \
  'https://item-management-api-dl6u.onrender.com/players/783/inventory' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "item_id": 3021,
  "quantity": 1
}'
Response:
204	Successful Response
4. 
curl -X 'POST' \
  'https://item-management-api-dl6u.onrender.com/players/783/inventory/3021/enchant' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "enchantment_id": 1
}'
Response:
204	Successful Response