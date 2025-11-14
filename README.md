# Item Management API
## Contributors:
Megan Robinson: mrobin47@calpoly.edu
Anna Huang: chuan133@calpoly.edu
Sameer Nadeem: monadeem@calpoly.edu
## Project Description:
For our project, we created a backend API for managing items in multiplayer games. Our backend service contains important item metadata like item ID, item display name, enchantments, weapon attack power, and rarity. This project provides a robust and scalable system for tracking global item data, player inventories, item quantities, applied enchantments, and various CRUD operations. This backend is useful for any multiplayer experience in which item data is changing and needs to be synchronized across each player’s instance of the game.
## Deployment

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the server

```bash
  uvicorn server:app --reload
```
