from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

import sqlalchemy

from src import database as db
from src.api import auth

router = APIRouter(
    prefix="",
    tags=["enchantments"],
    dependencies=[Depends(auth.get_api_key)],
)

class Enchantment(BaseModel):
    name: str
    effect_description: str

class EnchantmentResponse(BaseModel):
    message: str
    enchantment: Enchantment

class UpdateEnchantmentDescription(BaseModel):
    effect_description: str = Field(..., min_length=1, max_length=250)


@router.get("/enchantments", response_model=list[Enchantment])
def get_enchantments():
    with db.engine.begin() as connection:
        results = connection.execute(
            sqlalchemy.text(
                """
                SELECT enchantment_id, name, effect_description
                FROM enchantment
                ORDER BY enchantment_id
                """
            )
        ).fetchall()

    return [
        Enchantment(
            enchantment_id=row.enchantment_id,
            name=row.name,
            effect_description=row.effect_description
        )
        for row in results
    ]

@router.post("/enchantments", status_code=status.HTTP_201_CREATED, response_model=EnchantmentResponse)
def create_enchantment(enchantment: Enchantment):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO enchantment (name, effect_description, created_at)
                VALUES (:name, :effect_description, CURRENT_TIMESTAMP)
                ON CONFLICT (name) DO NOTHING
                RETURNING enchantment_id
                """
            ),
            {
                "name": enchantment.name,
                "effect_description": enchantment.effect_description
            }
        )
        new_enchantment_id = result.scalar()
        return {
            "message": f"Enchantment '{enchantment.name}' with ID {new_enchantment_id} created successfully",
            "enchantment": {
                "enchantment_id": new_enchantment_id,
                "name": enchantment.name,
                "effect_description": enchantment.effect_description
        }
    }

@router.delete("/enchantments/{enchantment_id}", response_model=dict[str, str])
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
            raise HTTPException(status_code=404, detail=f"Enchantment with ID {enchantment_id} not found")

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
        return {
            "message": f"Enchantment with ID {enchantment_id} deleted successfully"
        }

@router.put("/enchantments/{enchantment_id}/effect_description",  response_model=dict[str, str])
def update_enchantment_effect_description(enchantment_id: int, update: UpdateEnchantmentDescription):
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
            if not existing:
                raise HTTPException(status_code=404, detail=f"Enchantment with ID {enchantment_id} not found")

        connection.execute(
            sqlalchemy.text(
                """
                UPDATE enchantment
                SET effect_description = :effect_description,
                    created_at = CURRENT_TIMESTAMP
                WHERE enchantment_id = :enchantment_id
                """
            ),
            {
                "enchantment_id": enchantment_id,
                "effect_description": update.effect_description
            }
        )

    return {
        "message": f"Successfully updated enchantment {enchantment_id}'s effect description",
        "updated_effect_description": update.effect_description
    }
