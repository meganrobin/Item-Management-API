from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Union

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

class InventoryResponse(BaseModel):
    items: List[InventoryItem]
    message: str

@router.get("/{player_id}/inventory", response_model=Union[List[InventoryItem], Dict[str, Any]])
def get_inventory(player_id: str):
    with db.engine.begin() as connection:
        # First check if player exists
        player = connection.execute(
            sqlalchemy.text(
                """
                SELECT player_id FROM player WHERE player_id = :player_id
                """
            ),
            {"player_id": player_id}
        ).first()
        
        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Player with ID {player_id} not found"
            )
            
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
                LEFT JOIN item_enchantment ie ON ie.player_id = pii.player_id AND ie.item_id = pii.item_id
                LEFT JOIN enchantment e ON e.enchantment_id = ie.enchantment_id
                WHERE pii.player_id = :player_id
                GROUP BY pii.player_id, i.item_id, i.name, i.item_type, i.rarity, pii.quantity
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
    
    # For backward compatibility, return just the list if there are items
    if items:
        return items
    else:
        return {"message": f"Player {player_id} has no items in inventory", "items": []}

class ItemRequest(BaseModel):
    quantity: int = Field(gt=0)

@router.delete("/{player_id}/inventory/{item_id}", status_code=status.HTTP_200_OK, response_model=Dict[str, Any])
def delete_item(player_id: str, item_id: int, request: ItemRequest):
    with db.engine.begin() as connection:
        # Check if player exists
        player = connection.execute(
            sqlalchemy.text(
                """
                SELECT player_id FROM player WHERE player_id = :player_id
                """
            ),
            {"player_id": player_id}
        ).first()
        
        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Player with ID {player_id} not found"
            )
            
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
            return {
                "message": f"Removed all {request.quantity} '{item_name}' from player {player_id}'s inventory",
                "item_id": item_id,
                "quantity_removed": request.quantity,
                "remaining": 0
            }
        else:
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
            return {
                "message": f"Removed {request.quantity} '{item_name}' from player {player_id}'s inventory",
                "item_id": item_id,
                "quantity_removed": request.quantity,
                "remaining": new_quantity
            }

class AddItemRequest(BaseModel):
    item_id: int
    quantity: int = Field(gt=0)

@router.post("/{player_id}/inventory", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
def add_item(player_id: str, request: AddItemRequest):
    with db.engine.begin() as connection:
        # Check if player exists
        player = connection.execute(
            sqlalchemy.text(
                """
                SELECT player_id FROM player WHERE player_id = :player_id
                """
            ),
            {"player_id": player_id}
        ).first()
        
        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Player with ID {player_id} not found"
            )
            
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
            return {
                "message": f"Added {request.quantity} more '{item.name}' to player {player_id}'s inventory",
                "item_id": request.item_id,
                "name": item.name,
                "quantity_added": request.quantity,
                "total_quantity": new_quantity
            }
        else:
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
            return {
                "message": f"Added {request.quantity} '{item.name}' to player {player_id}'s inventory",
                "item_id": request.item_id,
                "name": item.name,
                "quantity_added": request.quantity,
                "total_quantity": request.quantity
            }

class EnchantRequest(BaseModel):
    enchantment_id: int

@router.post("/{player_id}/inventory/{item_id}/enchant", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
def enchant_item(player_id: str, item_id: int, request: EnchantRequest):
    with db.engine.begin() as connection:
        # Check if player exists
        player = connection.execute(
            sqlalchemy.text(
                """
                SELECT player_id FROM player WHERE player_id = :player_id
                """
            ),
            {"player_id": player_id}
        ).first()
        
        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Player with ID {player_id} not found"
            )
            
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
        existing_enchant = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1 FROM item_enchantment
                WHERE player_id = :player_id AND item_id = :item_id AND enchantment_id = :enchantment_id
                """
            ),
            {
                "player_id": player_id,
                "item_id": item_id,
                "enchantment_id": request.enchantment_id
            }
        ).first()

        if existing_enchant:
            return {
                "message": f"Enchantment '{enchant.name}' is already applied to '{inventory_row.name}'",
                "item_id": item_id,
                "item_name": inventory_row.name,
                "enchantment_id": request.enchantment_id,
                "enchantment_name": enchant.name
            }

        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO item_enchantment (player_id, item_id, enchantment_id)
                VALUES (:player_id, :item_id, :enchantment_id)
                ON CONFLICT DO NOTHING
                """
            ), 
            {
                "player_id": player_id,
                "item_id": item_id,
                "enchantment_id": request.enchantment_id
            }
        )
        
        return {
            "message": f"Successfully applied enchantment '{enchant.name}' to '{inventory_row.name}'",
            "item_id": item_id,
            "item_name": inventory_row.name,
            "enchantment_id": request.enchantment_id,
            "enchantment_name": enchant.name
        }

class CreatePlayerRequest(BaseModel):
    player_id: str
    username: str

@router.post("", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
def create_player(request: CreatePlayerRequest):
    """Create a new player."""
    with db.engine.begin() as connection:
        # Check if player already exists
        existing = connection.execute(
            sqlalchemy.text(
                """
                SELECT player_id FROM player
                WHERE player_id = :player_id
                """
            ),
            {"player_id": request.player_id}
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Player with ID {request.player_id} already exists"
            )

        # Create the player
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO player (player_id, username)
                VALUES (:player_id, :username)
                """
            ),
            {
                "player_id": request.player_id,
                "username": request.username
            }
        )
    
    return {
        "message": f"Player {request.username} created successfully with ID {request.player_id}",
        "player": {
            "player_id": request.player_id,
            "username": request.username
        }
    }