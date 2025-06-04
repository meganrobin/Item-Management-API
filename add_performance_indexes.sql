


CREATE INDEX IF NOT EXISTS idx_player_inventory_player_item 
ON player_inventory_item(player_id, item_id);

-- Index for player existence checks
CREATE INDEX IF NOT EXISTS idx_player_id 
ON player(player_id);

-- Index for item lookups (name retrieval, etc.)
CREATE INDEX IF NOT EXISTS idx_item_id 
ON item(item_id);

-- Index for enchantment lookups in the complex inventory query
CREATE INDEX IF NOT EXISTS idx_item_enchantment_pii_id 
ON item_enchantment(player_inventory_item_id);

-- Index for enchantment details
CREATE INDEX IF NOT EXISTS idx_enchantment_id 
ON enchantment(enchantment_id);

-- Composite index for inventory ordering (quantity desc, name asc)
CREATE INDEX IF NOT EXISTS idx_player_inventory_quantity 
ON player_inventory_item(player_id, quantity DESC);

-- Additional indexes for filtered queries
CREATE INDEX IF NOT EXISTS idx_item_type_rarity 
ON item(item_type, rarity);


SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE tablename IN ('player_inventory_item', 'player', 'item', 'item_enchantment', 'enchantment')
ORDER BY tablename, indexname;