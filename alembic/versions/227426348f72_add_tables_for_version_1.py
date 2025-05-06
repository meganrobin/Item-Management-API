"""Add tables for version 1

Revision ID: 227426348f72
Revises: 
Create Date: 2025-05-05 19:06:43.653849

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '227426348f72'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "player",
        sa.Column("player_id", sa.String, primary_key=True),
        sa.Column("username", sa.String, unique=True),
    )

    op.create_table(
        "item",
        sa.Column("item_id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("item_type", sa.String, nullable=False),
        sa.Column("rarity", sa.String, nullable=False)
    )

    op.create_table(
        "player_inventory_item",
        sa.Column("player_id", sa.String, sa.ForeignKey("player.player_id"), primary_key=True),
        sa.Column("item_id", sa.Integer, sa.ForeignKey("item.item_id"), primary_key = True),
        sa.Column("quantity", sa.Integer, nullable=False)
    )

    op.create_table(
        "item_enchantment",
        sa.Column("player_id", sa.String, sa.ForeignKey("player.player_id"), primary_key=True),
        sa.Column("item_id", sa.Integer, sa.ForeignKey("item.item_id"), primary_key = True),
        sa.Column("enchantment_id", sa.Integer, primary_key=True)
    )

    op.create_table(
        "enchantment",
        sa.Column("enchantment_id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("effect_description", sa.String, nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("enchantment")
    op.drop_table("item_enchantment")
    op.drop_table("player_inventory_item")
    op.drop_table("item")
    op.drop_table("player")
    
