# CQuests 1.6.6

A stability, performance and customisation release on top of 1.6.5. It adds no new gameplay. Quests, rewards, chapters, the farm, merchants and mail all behave exactly as in 1.6.5, and all player progress carries over.

## Upgrading from 1.6.5

1. Run `/cq backup` (or copy `plugins/CQuests/`).
2. Stop the server.
3. Replace `CQuests-1.6.5.jar` with `CQuests-1.6.6.jar` in `plugins/`. Keep the `plugins/CQuests/` folder.
4. Start the server. No config changes are needed; there are no new config keys.

Going back to 1.6.5 is the same steps in reverse. Names changed with `/cq character` are stored in `characters.yml`, which 1.6.5 already reads.

## Renaming NPCs everywhere

1.6.5 could rename NPCs, but the new name only showed on the name tag and in speech. Quest text, the boss bar, directions, mail and menus kept the old name. In 1.6.6 a rename reaches everything.

| Command | What it does |
|---|---|
| `/cq npc rename <id> <name>` | Rename a quest NPC. MiniMessage colours work, e.g. `<gold>Jerry` |
| `/cq character <id> name <name>` | Same, and also works for merchants (`flora`, ...) and Pip |
| `/cq character <id> title <text>` | The line under the name tag |
| `/cq character <id> prefix <text>` | Something before the name, e.g. `<red>★ ` (`none` clears it) |
| `/cq character <id> intro <line \| line>` | What the NPC says the first time you click it |
| `/cq character <id> idle <line \| line>` | What it says when it has nothing for you |
| `/cq character <id> reset` | Undo every change for that character |

* Works for operators in game **and from the server console** (1.6.5 was in game only).
* Where the new name shows: name tags, speech, `{npc:id}` mentions in quest descriptions, the boss bar ("Return to …"), the direction arrow, the journal and menus, letters and replies in `/quest mail` (including B.O.B's AI replies), the Sunflower Token messages for Flora, and admin messages.
* Commands keep working with either the id (`bob`) or the current name with dots and spaces ignored (`b.o.b`).
* `/cq npc list` now shows each id with its current name, e.g. `jerry (Farmer Jerold)`.
* Saved in `plugins/CQuests/characters.yml`. Ids, quests and player progress are never rewritten.
* Not covered: sentences you wrote yourself in `quests.yml` or `letters.yml` that contain an old name as plain text. Use `{npc:id}` there and it follows renames.

## Bugs fixed

* **NPCs that never spawned.** An NPC standing under a roof, a tree, leaves or inside a building failed the safety check and never appeared until a reload. Admin-chosen spots (`/cq npc place`, existing spawn points, merchant spawns) no longer need open sky. Random placement (`/cq scatter`, auto placement) still avoids caves.
* **One failed check blocked an NPC forever.** If a spot ever failed the safety check, the NPC stayed hidden until `/cq reload`. Now the spot is checked again every 5 minutes, so fixing the terrain is enough. A chunk that could not be read in time is simply retried instead of marking the spot unsafe.
* **Console spam.** The "Unsafe spawn for …" warning is logged once per NPC instead of on every check.
* **Small blocks at an NPC's feet.** Torches, carpets, flowers, pink petals, rails, buttons, levers, pressure plates, signs and banners no longer make a spot unsafe. Lava, water, fire and cobwebs still do.
* **Removed NPCs** left their old spot in the safety caches. They are cleaned up now.

## Less lag

* **Removed the server-wide mob movement listener.** 1.6.5 listened to `EntityMoveEvent` to stop NPCs being pushed. Just having that listener makes Paper create and fire an event for every moving mob on the server, every tick. An NPC that does get shoved (water, pistons, explosions) is now put back on its spot by the normal 3-second spawn check.
* **No repeated chunk scans.** Each NPC spot was re-validated with chunk snapshots (up to 4 chunks in the Nether and the End) every time a player walked back into range. A spot is now validated once, and a cheap live check of the floor and headroom on the region thread runs before each spawn.
* **Placing blocks is cheaper.** Every block placed anywhere wrote a second "already counted" mark into the chunk. That mark is now only written while the player has a `PLACE` quest that needs that block. The "you placed this yourself" protection for mining quests is unchanged.
* **Boss bar.** The tracker refreshes twice a second; it now skips rebuilding its text when the quest's progress has not changed.
* **Farm tool check.** The inventory scan for stray farm hoes runs every 2 seconds instead of every half second.
* **NPC lookups.** Name and id lookups (used by the tracker, directions, visibility and quest text many times a second) use a cached list instead of rebuilding every NPC and parsing its name on each call.

## Memory

* Players who are not online are saved and removed from memory during the regular one-minute autosave. Before, data loaded for admin commands on offline players (`/cq player …`, restores) and quit saves that raced with a late change (for example an AI mail reply arriving after the player left) stayed in memory until restart.

## Tested

* 133 unit tests, including new ones for dropping offline players from memory, decorations at an NPC's feet, and finding NPCs by id, name and original name.
* GitHub Actions builds the plugin and starts real servers: Paper 1.21.4 (with a test player that joins, talks to villagers, takes quests and checks the menus, End and Nether placement), the newest Paper and the newest Folia. The console renames an NPC, checks it in `/cq npc list` and resets it again. Any CQuests error or warning fails the run.
* The JAR attached to the release is the exact file built and tested in that run.
