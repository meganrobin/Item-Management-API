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

@router.get("/{player_id}/inventory", response_model=List[InventoryItem])
def get_inventory(player_id: str):
    with db.engine.begin() as connection:
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

    return [
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

class ItemRequest(BaseModel):
    quantity: int = Field(gt=0)

@router.delete("/{player_id}/inventory/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(player_id: str, item_id: int, request: ItemRequest):
    with db.engine.begin() as connection:
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
            
        if not result or result.quantity < request.quantity:
            raise HTTPException(status_code=404, detail="Not enough quantity")

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

        else:
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

class AddItemRequest(BaseModel):
    item_id: int
    quantity: int = Field(gt=0)

@router.post("/{player_id}/inventory", status_code=status.HTTP_201_CREATED)
def add_item(player_id: str, request: AddItemRequest):
    with db.engine.begin() as connection:
        existing = connection.execute(
            sqlalchemy.text(
                """
                SELECT player_id, item_id
                FROM player_inventory_item
                WHERE player_id = :player_id AND item_id = :item_id
                """
            ), 
            {"player_id": player_id, "item_id": request.item_id}
        ).first()

        if existing:
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

class EnchantRequest(BaseModel):
    enchantment_id: int

@router.post("/{player_id}/inventory/{item_id}/enchant", status_code=status.HTTP_201_CREATED)
def enchant_item(player_id: str, item_id: int, request: EnchantRequest):
    with db.engine.begin() as connection:
        inventory_row = connection.execute(
            sqlalchemy.text(
                """
                SELECT player_id, item_id
                FROM player_inventory_item
                WHERE player_id = :player_id AND item_id = :item_id
                """
            ),
            {
                "player_id": player_id,
                "item_id": item_id
            }
        ).first()

        if not inventory_row:
            raise HTTPException(status_code=404, detail="Item not found in inventory")

        enchant_exists = connection.execute(
            sqlalchemy.text(
                """
                SELECT enchantment_id 
                FROM enchantment 
                WHERE enchantment_id = :enchantment_id
                """
            ),
            {"enchantment_id": request.enchantment_id}
        ).first()

        if not enchant_exists:
            raise HTTPException(status_code=404, detail="Enchantment not found")

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
                "item_id": inventory_row.item_id,
                "enchantment_id": request.enchantment_id
            }
        )

class CreatePlayerRequest(BaseModel):
    player_id: str
    username: str

@router.post("", status_code=status.HTTP_201_CREATED)
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
    
    return {"message": f"Player {request.username} created successfully with ID {request.player_id}"}