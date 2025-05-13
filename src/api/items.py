from fastapi import APIRouter, Depends, HTTPException, status
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

class Enchantment(BaseModel):
    enchantment_id: int
    name: str
    effect_description: str

@router.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    with db.engine.begin() as connection:
        item = connection.execute(
            sqlalchemy.text(
                """
                SELECT id as item_id, name, item_type, rarity
                FROM item
                WHERE id = :item_id
                """
            ),
            {"item_id": item_id}
        ).first()

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Item with ID {item_id} not found in the database."
            )
    
    return Item(
        item_id=item.item_id,
        name=item.name,
        item_type=item.item_type,
        rarity=item.rarity
    )

@router.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(item: Item):
    with db.engine.begin() as connection:
        existing = connection.execute(
            sqlalchemy.text(
                """
                SELECT id FROM item
                WHERE id = :item_id
                """
            ),
            {"item_id": item.item_id}
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Item with ID {item.item_id} already exists"
            )

        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO item (id, name, item_type, rarity)
                VALUES (:item_id, :name, :item_type, :rarity)
                """
            ),
            {
                "item_id": item.item_id,
                "name": item.name,
                "item_type": item.item_type.value,
                "rarity": item.rarity
            }
        )

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    with db.engine.begin() as connection:
        existing = connection.execute(
            sqlalchemy.text(
                """
                SELECT id FROM item
                WHERE id = :item_id
                """
            ),
            {"item_id": item_id}
        ).first()

        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with ID {item_id} not found"
            )

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
                WHERE item_id = :item_id
                """
            ),
            {"item_id": item_id}
        )

        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM item
                WHERE id = :item_id
                """
            ),
            {"item_id": item_id}
        )

@router.post("/enchantments", status_code=status.HTTP_201_CREATED)
def create_enchantment(enchantment: Enchantment):
    with db.engine.begin() as connection:
        existing = connection.execute(
            sqlalchemy.text(
                """
                SELECT enchantment_id FROM enchantment
                WHERE enchantment_id = :enchantment_id
                """
            ),
            {"enchantment_id": enchantment.enchantment_id}
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Enchantment with ID {enchantment.enchantment_id} already exists"
            )

        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO enchantment (enchantment_id, name, effect_description)
                VALUES (:enchantment_id, :name, :effect_description)
                """
            ),
            {
                "enchantment_id": enchantment.enchantment_id,
                "name": enchantment.name,
                "effect_description": enchantment.effect_description
            }
        )

@router.delete("/enchantments/{enchantment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_enchantment(enchantment_id: int):
    with db.engine.begin() as connection:
        existing = connection.execute(
            sqlalchemy.text(
                """
                SELECT enchantment_id FROM enchantment
                WHERE enchantment_id = :enchantment_id
                """
            ),
            {"enchantment_id": enchantment_id}
        ).first()

        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enchantment with ID {enchantment_id} not found"
            )

        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM item_enchantment
                WHERE enchantment_id = :enchantment_id
                """
            ),
            {"enchantment_id": enchantment_id}
        )

        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM enchantment
                WHERE enchantment_id = :enchantment_id
                """
            ),
            {"enchantment_id": enchantment_id}
        )