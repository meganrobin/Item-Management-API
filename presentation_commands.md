SELECT pii.*, i.name 
FROM player_inventory_item pii 
JOIN item i ON pii.item_id = i.item_id 
WHERE pii.player_id = 1 AND pii.item_id = 5;

DROP INDEX IF EXISTS idx_player_inventory_player_item;

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) 
SELECT pii.*, i.name 
FROM player_inventory_item pii 
JOIN item i ON pii.item_id = i.item_id 
WHERE pii.player_id = 1 AND pii.item_id = 5;

CREATE INDEX idx_player_inventory_player_item 
ON player_inventory_item(player_id, item_id);

