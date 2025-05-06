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
1. The curl statement called. You can find this in the /docs site for your 
API under each endpoint. For example, for my site the /catalogs/ endpoint 
curl call looks like:
curl -X 'GET' \
    'https://item-management-api-dl6u.onrender.com/players' \
    -H 'accept: application/json'
2. The response you received in executing the curl statement

