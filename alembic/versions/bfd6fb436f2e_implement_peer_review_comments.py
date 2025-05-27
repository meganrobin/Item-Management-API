"""Implement peer review comments

Revision ID: bfd6fb436f2e
Revises: 227426348f72
Create Date: 2025-05-26 16:07:51.906428

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bfd6fb436f2e'
down_revision: Union[str, None] = '227426348f72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table("item_enchantment")
    op.drop_table("player_inventory_item")

    op.drop_table("enchantment")
    op.drop_table("item")
    op.drop_table("player")

    op.create_table(
        'player',
        sa.Column('player_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('username', sa.String, unique=True, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)
    )

    op.create_table(
        "item",
        sa.Column("item_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String, unique=True, nullable=False),
        sa.Column("item_type", sa.String, nullable=False),
        sa.Column("rarity", sa.String, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("item_type IN ('weapon', 'food', 'clothing')", name="check_item_type_valid"),
        sa.CheckConstraint("rarity IN ('common', 'uncommon', 'rare', 'epic', 'legendary')", name="check_rarity_valid")
    )

    op.create_table(
        "enchantment",
        sa.Column("enchantment_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String, unique=True, nullable=False),
        sa.Column("effect_description", sa.String, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)
    )

    op.create_table(
        "player_inventory_item",
        sa.Column("player_inventory_item_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("player_id", sa.Integer, sa.ForeignKey("player.player_id")),
        sa.Column("item_id", sa.Integer, sa.ForeignKey("item.item_id")),
        sa.Column("quantity", sa.Integer, nullable=False),
    )
    op.create_check_constraint("check_quantity_positive", "player_inventory_item", "quantity > 0")

    op.create_table(
        "item_enchantment",
        sa.Column("player_inventory_item_id", sa.Integer, sa.ForeignKey("player_inventory_item.player_inventory_item_id"), primary_key=True),
        sa.Column("enchantment_id", sa.Integer, sa.ForeignKey("enchantment.enchantment_id"), primary_key=True)
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_item_enchantment_enchantment_id", "item_enchantment", type_="foreignkey")
    op.drop_table('player')
    op.create_table(
        'player',
        sa.Column('player_id', sa.String, primary_key=True),
        sa.Column('username', sa.String, unique=True, nullable=True)
    )
    op.drop_constraint("check_quantity_positive", "player_inventory_item", type_="check")
    op.drop_table("item_enchantment")
    op.drop_column("player_inventory_item", "player_inventory_item_id")
