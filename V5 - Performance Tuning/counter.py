import sqlalchemy
import os
from dotenv import load_dotenv

load_dotenv()
POSTGRES_URI = os.getenv('POSTGRES_URI', 'postgresql+psycopg://myuser:mypassword2@localhost:5433/mydatabase')

def get_connection():
    engine = sqlalchemy.create_engine(POSTGRES_URI)
    return engine

def get_database_statistics():
    engine = get_connection()
    
    with engine.begin() as conn:
        player_count = conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM player")).scalar()
        item_count = conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM item")).scalar() 
        enchantment_count = conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM enchantment")).scalar()
        inventory_count = conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM player_inventory_item")).scalar()
        enchanted_items_count = conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM item_enchantment")).scalar()
        
        total_rows = player_count + item_count + enchantment_count + inventory_count + enchanted_items_count
        
        print(f"Generated enchantments: {enchanted_items_count}")
        
        print(f"\n=== FINAL DATA STATISTICS ===")
        print(f"Players: {player_count:,}")
        print(f"Items: {item_count:,}")
        print(f"Enchantments: {enchantment_count:,}")
        print(f"Player Inventory Items: {inventory_count:,}")
        print(f"Enchanted Items: {enchanted_items_count:,}")
        print(f"TOTAL ROWS: {total_rows:,}")

if __name__ == "__main__":
    get_database_statistics()