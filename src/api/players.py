from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List

import sqlalchemy
from enum import Enum

from src import database as db
from src.api import auth

router = APIRouter(
    prefix="/players",
    tags=["players"],
    dependencies=[Depends(auth.get_api_key)],
)

class ItemType(str, Enum):
    weapon = "weapon"
    food = "food"
    clothing = "clothing"

class InventoryItem(BaseModel):
    item_id: int
    name: str
    item_type: ItemType
    rarity: str
    quantity: int
    enchantments: List[str] = []

class ItemRequest(BaseModel):
    quantity: int = Field(gt=0)

class AddItemRequest(BaseModel):
    item_id: int
    quantity: int = Field(gt=0)

class EnchantRequest(BaseModel):
    enchantment_id: int

class CreatePlayerRequest(BaseModel):
    username: str

class InventoryResponse(BaseModel):
    items: List[InventoryItem]
    message: str

class RemoveItemResponse(BaseModel):
    message: str
    item_id: int
    quantity_removed: int
    remaining: int

class AddItemResponse(BaseModel):
    message: str
    item_id: int
    name: str
    quantity_added: int
    total_quantity: int

class EnchantItemResponse(BaseModel):
    message: str
    item_id: int
    item_name: str
    enchantment_id: int
    enchantment_name: str

class PlayerInfo(BaseModel):
    player_id: int
    username: str

class CreatePlayerResponse(BaseModel):
    message: str
    player: PlayerInfo

class RemoveEnchantmentsResponse(BaseModel):
    message: str
    item_id: int
    player_id: int

# Helper function to check if a player exists in the database
def check_player_exists(connection, player_id: int):
    player = connection.execute(
        sqlalchemy.text("SELECT player_id FROM player WHERE player_id = :player_id"),
        {"player_id": player_id}
    ).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {player_id} not found"
        )
    return player

# Returns a player's inventory
@router.get("/{player_id}/inventory", response_model=InventoryResponse)
def get_inventory(player_id: int):
    with db.engine.begin() as connection:
        # First check if player exists
        check_player_exists(connection, player_id)
            
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT pii.player_id,
                i.item_id AS item_id,
                i.name,
                i.item_type,
                i.rarity,
                pii.quantity,
                COALESCE(array_agg(e.name) FILTER (WHERE e.name IS NOT NULL), '{}') AS enchantments
                FROM player_inventory_item pii
                JOIN item i ON pii.item_id = i.item_id
                LEFT JOIN item_enchantment ie ON ie.player_inventory_item_id = pii.player_inventory_item_id
                LEFT JOIN enchantment e ON e.enchantment_id = ie.enchantment_id
                WHERE pii.player_id = :player_id
                GROUP BY pii.player_id, i.item_id, i.name, i.item_type, i.rarity, pii.quantity
                ORDER BY pii.quantity DESC, i.name ASC

                """
            ), 
            {"player_id": player_id}
        ).fetchall()

    items = [
        InventoryItem(
            item_id=row.item_id,
            name=row.name,
            item_type=row.item_type,
            rarity=row.rarity,
            quantity=row.quantity,
            enchantments=row.enchantments
        )
        for row in result
    ]
    
    msg = f"Player {player_id} has {len(items)} item(s) in their inventory."
    return InventoryResponse(items=items, message=msg)

# Allows the player to remove items from their inventory
@router.patch("/{player_id}/inventory/{item_id}", status_code=status.HTTP_200_OK, response_model=RemoveItemResponse)
def remove_item_quantity(player_id: int, item_id: int, request: ItemRequest):
    with db.engine.connect().execution_options(isolation_level="REPEATABLE READ") as connection:
        with connection.begin():
            # Check if player exists
            check_player_exists(connection, player_id)
                
            # Check if item exists in inventory
            result = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT player_id, item_id, quantity
                    FROM player_inventory_item
                    WHERE player_id = :player_id AND item_id = :item_id
                    """
                ), 
                {"player_id": player_id, "item_id": item_id}
            ).first()
                
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail=f"Item with ID {item_id} not found in player {player_id}'s inventory"
                )
                
            if result.quantity < request.quantity:
                raise HTTPException( 
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"Not enough quantity available. Requested: {request.quantity}, Available: {result.quantity}"
                )

            # Get item name for the response message
            item_name = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT name FROM item WHERE item_id = :item_id
                    """
                ),
                {"item_id": item_id}
            ).scalar()

            # Removes the items from the player's inventory
            if result.quantity == request.quantity:
                connection.execute(
                    sqlalchemy.text(
                        """
                        DELETE FROM player_inventory_item
                        WHERE player_id = :player_id AND item_id = :item_id
                        """
                    ), 
                    {"player_id": player_id, "item_id": item_id}
                )
                return RemoveItemResponse(
                    message=f"Removed all {request.quantity} '{item_name}' from player {player_id}'s inventory",
                    item_id=item_id,
                    quantity_removed=request.quantity,
                    remaining=0
                )
            else:
                # Update the item's quantity in the player's inventory
                new_quantity = result.quantity - request.quantity
                connection.execute(
                    sqlalchemy.text(
                        """
                        UPDATE player_inventory_item 
                        SET quantity = quantity - :quantity
                        WHERE player_id = :player_id AND item_id = :item_id
                        """
                    ), 
                    {
                        "player_id": player_id,
                        "item_id": item_id,
                        "quantity": request.quantity
                    }
                )
                return RemoveItemResponse(
                    message=f"Removed {request.quantity} '{item_name}' from player {player_id}'s inventory",
                    item_id=item_id,
                    quantity_removed=request.quantity,
                    remaining=new_quantity
                )

# Allow the player to add an item to their inventory
@router.post("/{player_id}/inventory", status_code=status.HTTP_201_CREATED, response_model=AddItemResponse)
def add_item(player_id: int, request: AddItemRequest):
    with db.engine.begin() as connection:
        # Check if player exists
        check_player_exists(connection, player_id)
            
        # Check if item exists
        item = connection.execute(
            sqlalchemy.text(
                """
                SELECT item_id, name FROM item WHERE item_id = :item_id
                """
            ),
            {"item_id": request.item_id}
        ).first()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with ID {request.item_id} not found"
            )

        existing = connection.execute(
            sqlalchemy.text(
                """
                SELECT player_id, item_id, quantity
                FROM player_inventory_item
                WHERE player_id = :player_id AND item_id = :item_id
                """
            ), 
            {"player_id": player_id, "item_id": request.item_id}
        ).first()

        if existing:
            # If the item is already in the player's inventory
            new_quantity = existing.quantity + request.quantity
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE player_inventory_item
                    SET quantity = quantity + :quantity
                    WHERE player_id = :player_id AND item_id = :item_id
                    """
                ), 
                {
                    "quantity": request.quantity,
                    "player_id": player_id,
                    "item_id": request.item_id
                }
            )
            return AddItemResponse(
                message=f"Added {request.quantity} more '{item.name}' to player {player_id}'s inventory",
                item_id=request.item_id,
                name=item.name,
                quantity_added=request.quantity,
                total_quantity=new_quantity
            )
        else:
            # If the item isn't already in the player's inventory
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO player_inventory_item (player_id, item_id, quantity)
                    VALUES (:player_id, :item_id, :quantity)
                    """
                ), 
                {
                "player_id": player_id,
                "item_id": request.item_id,
                "quantity": request.quantity
                }
            )
            return AddItemResponse(
                message=f"Added {request.quantity} '{item.name}' to player {player_id}'s inventory",
                item_id=request.item_id,
                name=item.name,
                quantity_added=request.quantity,
                total_quantity=request.quantity
            )

# Allows the player to enchant an item
@router.post("/{player_id}/inventory/{item_id}/enchant", status_code=status.HTTP_201_CREATED, response_model=EnchantItemResponse)
def enchant_item(player_id: str, item_id: int, request: EnchantRequest):
    with db.engine.connect().execution_options(isolation_level="SERIALIZABLE") as connection:
        with connection.begin():
            # Check if player exists
            check_player_exists(connection, player_id)
                
            inventory_row = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT pii.player_id, pii.item_id, i.name
                    FROM player_inventory_item pii
                    JOIN item i ON pii.item_id = i.item_id
                    WHERE pii.player_id = :player_id AND pii.item_id = :item_id
                    """
                ),
                {
                    "player_id": player_id,
                    "item_id": item_id
                }
            ).first()

            if not inventory_row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail=f"Item with ID {item_id} not found in player {player_id}'s inventory"
                )

            enchant = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT enchantment_id, name
                    FROM enchantment 
                    WHERE enchantment_id = :enchantment_id
                    """
                ),
                {"enchantment_id": request.enchantment_id}
            ).first()

            if not enchant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail=f"Enchantment with ID {request.enchantment_id} not found"
                )

            # Check if enchantment already exists
            inventory_row = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT pii.player_inventory_item_id, i.name
                    FROM player_inventory_item pii
                    JOIN item i ON pii.item_id = i.item_id
                    WHERE pii.player_id = :player_id AND pii.item_id = :item_id
                    """
                ),
                {"player_id": player_id, "item_id": item_id}
            ).first()

            if not inventory_row:
                raise HTTPException(status_code=404, detail="Item not found in inventory")

            player_inventory_item_id = inventory_row.player_inventory_item_id
            item_name = inventory_row.name

            existing_enchant = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT 1 FROM item_enchantment
                    WHERE player_inventory_item_id = :pii_id AND enchantment_id = :enchantment_id
                    """
                ),
                {
                    "pii_id": player_inventory_item_id,
                    "enchantment_id": request.enchantment_id
                }
            ).first()

            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO item_enchantment (player_inventory_item_id, enchantment_id)
                    VALUES (:pii_id, :enchantment_id)
                    ON CONFLICT DO NOTHING
                    """
                ),
                {
                    "pii_id": player_inventory_item_id,
                    "enchantment_id": request.enchantment_id
                }
            )
            return EnchantItemResponse(
                message=f"Successfully applied enchantment '{enchant.name}' to '{inventory_row.name}'",
                item_id=item_id,
                item_name=inventory_row.name,
                enchantment_id=request.enchantment_id,
                enchantment_name=enchant.name
            )

# Allows for the creation of new players
@router.post("", status_code=status.HTTP_201_CREATED, response_model=CreatePlayerResponse)
def create_player(request: CreatePlayerRequest):
    """Create a new player."""
    with db.engine.begin() as connection:
        # Check if username exists
        existing = connection.execute(
            sqlalchemy.text(
                """
                SELECT username FROM player
                WHERE username = :username
                """
            ),
            {"username": request.username}
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Player with username {request.username} already exists"
            )

        # Create the player
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO player (username, created_at)
                VALUES (:username, CURRENT_TIMESTAMP)
                RETURNING player_id
                """
            ),
            {
                "username": request.username
            }
        )
        new_player_id = result.scalar()
    
    return CreatePlayerResponse(
        message=f"Player {request.username} created successfully with ID {new_player_id}",
        player=PlayerInfo(player_id=new_player_id, username=request.username)
    )

# Allows the player to delete an item's enchantment
@router.delete("/{player_id}/inventory/{item_id}/enchantments", status_code=status.HTTP_200_OK, response_model=RemoveEnchantmentsResponse)
def remove_enchantments(player_id: str, item_id: int):
    with db.engine.connect().execution_options(isolation_level="SERIALIZABLE") as connection:
        with connection.begin():
            check_player_exists(connection, player_id)

            # Get player_inventory_item_id
            inventory_row = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT player_inventory_item_id, item_id FROM player_inventory_item
                    WHERE player_id = :player_id AND item_id = :item_id
                    """
                ),
                {"player_id": player_id, "item_id": item_id}
            ).first()

            if not inventory_row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Item with ID {item_id} not found in player {player_id}'s inventory"
                )

            pii_id = inventory_row.player_inventory_item_id

            # Delete enchantment for this item
            deleted = connection.execute(
                sqlalchemy.text(
                    """
                    DELETE FROM item_enchantment
                    WHERE player_inventory_item_id = :pii_id
                    """
                ),
                {"pii_id": pii_id}
            )

            return RemoveEnchantmentsResponse(
                message=f"Successfully removed enchantment from item ID {item_id} for player {player_id}.",
                item_id=item_id,
                player_id=player_id
            )