# Letters, field discoveries and editable characters

Keep the existing `plugins/CQuests` folder when upgrading. Stop the server and back it up before replacing the JAR. Existing quest IDs, decisions, XP, hoe unlocks, NPC placements and merchant routes are retained.

## Letters and consequences

- `/quest mail` opens your private, paginated mailbox. Click a letter to read its book; it stays available for rereading. The sunflower at the bottom shows your discovery pouch.
- Letters unlock from actual saved meetings, completed quests, decisions and wheat harvests. There are no repeatable mail rewards. Reading, reopening and reconnecting do not mint currency.
- Stephan welcomes players he has met. Steve writes differently depending on the promise made to Martha. Ned responds to the courier decision made to Lucy. Pip writes after Scarecrow Watch, and remembers the Martha decision when he accompanies you later.
- Flora writes after your first sunflower discovery. Lucy's lost button and B.O.B's old field marker add small story discoveries at 3,000 and 10,000 wheat. These are collection/story entries, rather than physical quest items.
- `letters.yml` controls the sender, subject, body and conditions for every letter. Conditions combine: `quest`, `decision` (`kind`/`selfish`), `met`, and `wheat`. An omitted condition imposes no requirement. `{player}` inserts the reader's name. Keep letter IDs stable to preserve read status. Apply file edits with `/cq reload`.

Consequences are personal story reactions. Existing decisions do not penalise unrelated players, change their quest progress, or make villagers hostile. Family reactions from 1.4.0 remain in `memories.yml`.

## Sunflower discoveries

- Each 750 successfully harvested wheat in a configured farm earns one Sunflower Token. Invalid crops, duplicate hits during regrowth and wheat outside the farm do not advance the counter.
- `/quest discoveries` shows the collection, available tokens and distance to the next token. `%cquests_sunflowers%` is available through PlaceholderAPI.
- Tokens are automatically banked against the player's UUID. Their sunflower icon appears in the mailbox and merchant editor. They are not a transferable inventory item: ordinary or renamed sunflowers, copied GUI icons and death drops cannot become currency.
- Existing recorded farm harvests count toward the milestones. Story resets retain spent tokens, so resetting quests cannot reclaim them.
- Read state and token spending use the existing ordered player saves. A graceful restart preserves them. Player inventory, external economy balances and plugin saves do not form a shared crash-atomic database transaction; this does not promise immunity to abrupt host rollback.

## Place Flora, the sixth merchant

Flora is added as a disabled merchant preset; existing merchants are kept. Her starting offers cost 1 token for 16 golden carrots, 3 for 16 experience bottles, 8 for a name tag, and 12 for a bell. These are editable examples.

1. Stand at her arrival point: `/cq merchant spawn flora`.
2. Get her trail wand: `/cq merchant wand flora`.
3. Right-click safe ground along the route. Keep consecutive points within 32 blocks.
4. Stand at her store, face the direction she should face, and use `/cq merchant end flora`.
5. She walks to the store and opens trading on arrival. `/cq merchant test flora` gives an OP a temporary private preview without trading or changing the real route.

Crouch-click Flora as an OP, or use `/cq merchant edit flora`. Select the sunflower at slot 33, then use the existing amount buttons to change the token price. Select the gold ingot to change the Vault money price. Item costs, money and tokens can be combined. Zero disables that component of the price. Save before selecting a different offer.

Trading checks the current offer revision, reach, available tokens, exact item costs and complete reward capacity before applying the purchase. The normal one-confirmation and cooldown guards remain. Non-OPs cannot edit, even with wildcard permissions. Flora speaks privately before opening the market; click again to advance the conversation.

## Character customisation

Quest NPCs, all six merchants and Pip support per-character overrides in `characters.yml`. The in-game editor commands require an actual OP:

```text
/cq character bob name <gold>B.O.B
/cq character bob prefix <gray>[Archivist] </gray>
/cq character bob title Keeper of the old records
/cq character bob format <prefix><yellow><bold><name></bold>\n<gray>LEVEL <aqua><level>
/cq character bob speech-prefix <gold><name></gold><gray> says: </gray>
/cq character bob intro We have not met. | Call me B.O.B.
/cq character bob idle Looking for another story? | I remember that old road.
/cq character flora name <yellow>Flora the Fieldkeeper
/cq character flora idle Found a little sunshine, {player}? | Show me what you brought.
/cq character pip arrival Steve told me what happened. I'll walk with you.
/cq character bob prefix none
/cq character bob reset
```

Use real quest NPC/merchant IDs, with `pip` for the companion. `/cq npc rename <id> <name>` uses the same saved name override. Names can contain capitals and dots. MiniMessage and the existing text parser are used for colours. `none` clears a prefix. `reset` removes only that character's overrides; it does not reset progress, routes or trades.

Nameplate placeholders: `<prefix>`, `<name>`, `<title>`, `<level>`. In merchant nameplates `<title>` is the current shop status and `<level>` is 0; merchants do not acquire quest-level gates. Use actual newlines in YAML double-quoted `format` values to make a two-line plate. Global uppercase behaviour remains controlled by `npc.uppercase-names`.

`intro` changes first-meeting dialogue; `idle` changes idle dialogue. Merchant `idle` is their pre-shop conversation. `arrival` changes Pip's arrival line. Quest-specific offer/completion speeches remain editable in `quests.yml`; decision and family speeches remain in `memories.yml`. Character edits affect the next conversation and refresh existing labels. Pip's existing nameplate height and owner-only visibility remain in place.

The file writer saves character changes in order and drains on shutdown. Use `/cq reload` after direct YAML edits. Keep IDs stable when editing configuration.
