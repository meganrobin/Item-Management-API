from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

import sqlalchemy

from src import database as db
from src.api import auth

router = APIRouter(
    prefix="",
    tags=["items"],
    dependencies=[Depends(auth.get_api_key)],
)

class ItemType(str, Enum):
    weapon = "weapon"
    food = "food"
    clothing = "clothing"

class Item(BaseModel):
    item_id: int
    name: str
    item_type: ItemType
    rarity: str

class ItemWithoutID(BaseModel):
    name: str
    item_type: ItemType
    rarity: str

class Enchantment(BaseModel):
    enchantment_id: int
    name: str
    effect_description: str

class UpdateEnchantmentDescription(BaseModel):
    effect_description: str = Field(..., min_length=1, max_length=250)

class ItemResponse(BaseModel):
    message: str
    item: Item

# Returns all items in the database
@router.get("/items", response_model=list[Item])
def get_items(
    item_type: Optional[ItemType] = Query(None, description="Filter by item type"),
    rarity: Optional[str] = Query(None, description="Filter by item rarity"),
):
    base_query = """
        SELECT item_id, name, item_type, rarity
        FROM item
    """
    
    filters = []
    params = {}

    # Allows for filtering by item_type and rarity
    if item_type is not None:
        filters.append("item_type = :item_type")
        params["item_type"] = item_type.value

    if rarity is not None:
        filters.append("rarity = :rarity")
        params["rarity"] = rarity

    if filters:
        base_query += " WHERE " + " AND ".join(filters)
    
    base_query += " ORDER BY item_id"

    with db.engine.begin() as connection:
        results = connection.execute(sqlalchemy.text(base_query), params).fetchall()

    return [
        Item(
            item_id=row.item_id,
            name=row.name,
            item_type=row.item_type,
            rarity=row.rarity
        )
        for row in results
    ]

# Returns a specific item's information such as item_id, name, item_type and rarity
@router.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    with db.engine.begin() as connection:
        item = connection.execute(
            sqlalchemy.text(
                """
                SELECT item_id, name, item_type, rarity
                FROM item
                WHERE item_id = :item_id
                """
            ),
            {"item_id": item_id}
        ).first()

        if not item:
            raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

    
    return Item(
        item_id=item.item_id,
        name=item.name,
        item_type=item.item_type,
        rarity=item.rarity
    )

# Creates a new item
@router.post("/items", status_code=status.HTTP_201_CREATED, response_model=ItemResponse)
def create_item(item: ItemWithoutID):
    with db.engine.begin() as connection:
        # Checks if the item is already in the database
        existing = connection.execute(
            sqlalchemy.text(
                """
                SELECT name, item_type, rarity FROM item
                WHERE name = :name AND item_type = :item_type AND rarity = :rarity
                """
            ),
            {
                "name": item.name,
                "item_type": item.item_type,
                "rarity": item.rarity
            }
        ).first()

        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Item with name {item.name}, type {item.item_type.value}, and rarity {item.rarity} already exists"
            )
            
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO item (name, item_type, rarity, created_at)
                VALUES (:name, :item_type, :rarity, CURRENT_TIMESTAMP)
                RETURNING item_id
                """
            ),
            {
                "name": item.name,
                "item_type": item.item_type.value,
                "rarity": item.rarity
            }
        )
        new_item_id = result.scalar()

    return {
        "message": f"Item '{item.name}' with ID {new_item_id} created successfully",
        "item": {
            "item_id": new_item_id,
            "name": item.name,
            "item_type": item.item_type,
            "rarity": item.rarity
        }
    }

# Deletes the specified item
@router.delete("/items/{item_id}", response_model=dict[str, str])
def delete_item(item_id: int):
    with db.engine.begin() as connection:
        # Checks if the item is in the database
        existing = connection.execute(
            sqlalchemy.text(
                """
                SELECT item_id FROM item
                WHERE item_id = :item_id
                """
            ),
            {"item_id": item_id}
        ).first()

        if not existing:
            raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM player_inventory_item
                WHERE item_id = :item_id
                """
            ),
            {"item_id": item_id}
        )
        
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM item_enchantment
                WHERE player_inventory_item_id IN (
                    SELECT player_inventory_item_id
                    FROM player_inventory_item
                    WHERE item_id = :item_id
                )
                """
            ),
            {"item_id": item_id}
        )

        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM item
                WHERE item_id = :item_id
                """
            ),
            {"item_id": item_id}
        )
        return {
            "message": f"Item with ID {item_id} deleted successfully"
        }
