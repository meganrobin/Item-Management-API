import sqlalchemy
from faker import Faker
import random
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()
POSTGRES_URI = os.getenv('POSTGRES_URI', 'postgresql+psycopg://myuser:mypassword2@localhost:5433/mydatabase')

def get_connection():
    engine = sqlalchemy.create_engine(POSTGRES_URI, use_insertmanyvalues=True)
    return engine

def generate_fake_data():
    fake = Faker()
    engine = get_connection()
    
    print("Starting fake data generation...")
    
    num_players = 100000
    num_items = 1000
    num_enchantments = 500
    
    with engine.begin() as conn:
        print("Generating players...")
        players = []
        for i in range(num_players):
            if i % 1000 == 0:
                print(f"Players: {i}/{num_players}")
            
            players.append({
                "username": fake.unique.user_name() + str(i),  
            })
        
        conn.execute(
            sqlalchemy.text("""
                INSERT INTO player (username, created_at) 
                VALUES (:username, CURRENT_TIMESTAMP)
            """), 
            players
        )
        
        print("Generating items...")
        items = []
        item_types = ['weapon', 'food', 'clothing']
        rarities = ['common', 'uncommon', 'rare', 'epic', 'legendary']
        rarity_weights = [0.5, 0.25, 0.15, 0.08, 0.02] 
        
        for i in range(num_items):
            item_type = random.choice(item_types)
            rarity = np.random.choice(rarities, p=rarity_weights)
            
            items.append({
                "name": f"{fake.word().title()} {item_type.title()} {i}",
                "item_type": item_type,
                "rarity": rarity
            })
        
        conn.execute(
            sqlalchemy.text("""
                INSERT INTO item (name, item_type, rarity, created_at) 
                VALUES (:name, :item_type, :rarity, CURRENT_TIMESTAMP)
            """),
            items
        )
        
        print("Generating enchantments...")
        enchantments = []
        enchantment_effects = [
            "Increases damage by 10%",
            "Adds fire damage",
            "Increases critical hit chance",
            "Restores health on hit",
            "Increases movement speed",
            "Adds poison damage",
            "Reduces stamina consumption",
            "Increases armor penetration",
            "Adds lightning damage",
            "Increases luck"
        ]
        
        for i in range(num_enchantments):
            enchantments.append({
                "name": f"{fake.word().title()} {random.choice(['Blessing', 'Curse', 'Enhancement', 'Aura'])} {i}",
                "effect_description": random.choice(enchantment_effects)
            })
        
        conn.execute(
            sqlalchemy.text("""
                INSERT INTO enchantment (name, effect_description, created_at) 
                VALUES (:name, :effect_description, CURRENT_TIMESTAMP)
            """),
            enchantments
        )
        
        print("Generating player inventory items...")
        batch_size = 5000
        total_inventory_items = 0
        
        for player_batch_start in range(1, num_players + 1, 1000):
            player_batch_end = min(player_batch_start + 999, num_players)
            inventory_items = []
            
            for player_id in range(player_batch_start, player_batch_end + 1):
                num_player_items = random.randint(50, 150)
                
                for _ in range(num_player_items):
                    item_id = random.randint(1, num_items)
                    quantity = random.choices(
                        [1, 2, 3, 4, 5, 10, 20, 50], 
                        weights=[0.4, 0.25, 0.15, 0.1, 0.05, 0.03, 0.015, 0.005]
                    )[0]
                    
                    inventory_items.append({
                        "player_id": player_id,
                        "item_id": item_id,
                        "quantity": quantity
                    })
                    total_inventory_items += 1
            
            for i in range(0, len(inventory_items), batch_size):
                batch = inventory_items[i:i + batch_size]
                conn.execute(
                    sqlalchemy.text("""
                        INSERT INTO player_inventory_item (player_id, item_id, quantity) 
                        VALUES (:player_id, :item_id, :quantity)
                        ON CONFLICT DO NOTHING
                    """),
                    batch
                )
            
            print(f"Processed players {player_batch_start}-{player_batch_end}, Total inventory items so far: {total_inventory_items}")
        
        print("Generating item enchantments...")
        pii_ids = conn.execute(
            sqlalchemy.text("SELECT player_inventory_item_id FROM player_inventory_item")
        ).fetchall()
        
        enchantment_records = []
        for pii_id_row in pii_ids:
            if random.random() < 0.3:  # 30% chance of enchantment
                enchantment_id = random.randint(1, num_enchantments)
                enchantment_records.append({
                    "player_inventory_item_id": pii_id_row[0],
                    "enchantment_id": enchantment_id
                })
        
        # Insert enchantments in batches
        for i in range(0, len(enchantment_records), batch_size):
            batch = enchantment_records[i:i + batch_size]
            conn.execute(
                sqlalchemy.text("""
                    INSERT INTO item_enchantment (player_inventory_item_id, enchantment_id) 
                    VALUES (:player_inventory_item_id, :enchantment_id)
                    ON CONFLICT DO NOTHING
                """),
                batch
            )
        
        print(f"Generated enchantments: {len(enchantment_records)}")
        
        player_count = conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM player")).scalar()
        item_count = conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM item")).scalar() 
        enchantment_count = conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM enchantment")).scalar()
        inventory_count = conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM player_inventory_item")).scalar()
        enchanted_items_count = conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM item_enchantment")).scalar()
        
        total_rows = player_count + item_count + enchantment_count + inventory_count + enchanted_items_count
        
        print(f"\n=== FINAL DATA STATISTICS ===")
        print(f"Players: {player_count:,}")
        print(f"Items: {item_count:,}")
        print(f"Enchantments: {enchantment_count:,}")
        print(f"Player Inventory Items: {inventory_count:,}")
        print(f"Enchanted Items: {enchanted_items_count:,}")
        print(f"TOTAL ROWS: {total_rows:,}")

if __name__ == "__main__":
    generate_fake_data()