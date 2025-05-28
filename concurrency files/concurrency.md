Case 1:
Type: Phantom Read
If our service didn’t have concurrency control protection in place, the following scenario could occur: A player’s game calls GET /players/{player_id}/inventory to list items. While the transaction is running, another player’s game adds a new item with POST /players/{player_id}/inventory. So phantom rows will appear.
What we did to ensure isolation of our transactions: we used the SERIALIZABLE isolation level in the POST /players/{player_id}/inventory endpoint.

Case 2:
Type: Non-Repeatable Read
If our service didn’t have concurrency control protection in place, the following scenario could occur: A player’s game calls PATCH /players/{player_id}/inventory/{item_id} to remove items, reading the quantity twice in the same transaction. Meanwhile, another player’s game adds items with POST /players/{player_id}/inventory.
What we did to ensure isolation of our transactions: we used the REPEATABLE READ isolation level in the PATCH /players/{player_id}/inventory/{item_id}. 

Case 3:
Type: Lost Update
If our service didn’t have concurrency control protection in place, the following scenario could occur: Two clients act on the same inventory item at the same time: (i) one calls POST /players/{player_id}/inventory/{item_id}/enchant to add an enchantment, (ii) the other calls DELETE /players/{player_id}/inventory/{item_id}/enchantments to remove all enchantments. Without concurrency control, the add and remove can interleave, causing the newly added enchantment to be lost.
What we did to ensure isolation of our transactions: we used the SERIALIZABLE isolation level in both POST /players/{player_id}/inventory/{item_id}/enchant and DELETE /players/{player_id}/inventory/{item_id}/enchantments.
