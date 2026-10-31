# CQuests

A villager quest plugin for **Paper, Folia, Leaf and Purpur 1.21.4+**, built for Java and Bedrock (Geyser) players alike.

100 story villagers tell one linked story over 5 chapters, every villager has 10,000 side quests (1,000,000 in total), one villager gives a daily quest, and finishing the journey plays an ending cinematic, gives a custom achievement and a book of your own story. No resource pack or datapack is needed.

## Install

1. Download `CQuests-<version>.jar` from the latest build (GitHub Actions, "Build" workflow, artifact) and put it in `plugins/`.
2. Make sure you have an economy plugin with `/eco give` (EssentialsX works). Change `money-command` in `config.yml` if yours is different.
3. Start the server. The 15 spawn villagers are placed around the world spawn automatically, the rest further out.
4. Give players the quest command: `/lp group default permission set quests.use true`
5. Optional: move the villagers to your own spots (see "Placing villagers").

WorldGuard, Floodgate and Geyser are optional. NPCs spawn even inside regions with `mob-spawning deny`.

## Commands

| Command | Who | What it does |
|---|---|---|
| `/quests` | `quests.use` | Quest menu: chapter progress, active quests, chapters, tracker toggle |
| `/quests book` | `quests.use` | The journal book with every quest and the "All Quests" pages |
| `/quests list` | `quests.use` | Active quests in chat |
| `/quests track` | `quests.use` | Turn the boss bar tracker on or off |
| `/quests story` | `quests.use` | Read your story book again after finishing the journey |
| `/quests abandon <quest>` | `quests.use` | Drop a side or daily quest |
| `/cq reload` | op | Reload config, NPCs and quests |
| `/cq npc list` | op | All NPCs and where they stand |
| `/cq npc place <id>` | op | Put an NPC where you stand |
| `/cq npc remove <id>` | op | Take an NPC off the map |
| `/cq npc tp <id>` | op | Teleport to an NPC |
| `/cq pos1`, `/cq pos2` | op | Select a box to scatter NPCs in |
| `/cq scatter <ids, act1, act2 or all> [region] [world]` | op | Spread NPCs in a WorldGuard region or your box. They keep wandering inside it |
| `/cq player <name> reset` | op | Wipe a player's quest progress |
| `/cq player <name> complete <quest>` | op | Mark a quest done |
| `/cq player <name> give <quest>` | op | Give a quest |
| `/cq player <name> resetdaily` | op | Let a player do the daily again now |
| `/cq quest <id>` | op | Show a quest's details |
| `/cq finale [player]` | op | Preview the ending (no rewards) |
| `/cq backup` | op | Back up all quest data now |
| `/cq backups` | op | List backups, newest first |
| `/cq restore <backup or latest> <player or all>` | op | Put quest data back from a backup |

Aliases: `/quest`, `/q`, `/journal` and `/cq` for `/cquests`.

## Permissions

| Permission | Default | |
|---|---|---|
| `quests.use` | nobody | Use `/quests`. Give it to your default group |
| `cquests.admin` | op | All `/cq` commands |
| `cquests.bypass` | nobody | Build and PvP inside the protected area around villagers |

Clicking villagers and doing quests needs no permission.

## For players

1. Join. A short guide shows up and your first quest starts: talk to **Villager Stephan** near spawn.
2. Click a villager with a white name to talk, click again to accept its quest.
3. The bar at the top of your screen tells you what to do next. `/quests` shows all your quests.
4. The first few story steps go straight from villager to villager. After that each villager wants some side jobs done before the story moves on.

## How it plays

* **Click a villager** to talk. It offers a quest; click again (or the [Accept] button) to take it. All villager chat goes only to the player talking to it.
* **The story** is 101 quests in 5 chapters. Before each story step opens you have to do side quests for the previous villager, and the first quest of every new chapter needs 20. Every 5th step is a short one. Getting through one chapter takes a long time on purpose.
* **Side quests** are generated from `generator.yml`: kill, mine, harvest, fish, breed, tame, shear, craft, smelt, enchant, eat, deliver and place quests, getting harder and paying more as you go. Bigger quests pay more.
* **Daily quest**: Marigold gives one job every 24 hours for 10,000.
* **Rewards** are money plus normal items. No elytra, dragon eggs, god apples, totems, beacons or nether stars. Netherite only from level 85 quests. Some side quests give a potion effect like 1 hour of Swiftness.
* **Finished villagers disappear**: once you've done everything a villager has for you, you stop seeing it, so the spawn gets less crowded as you go.
* **Animations**: big quests and chapter ends play a particle helix, a typed out title, music and fireworks, then the next chapter card. The last quest plays a camera tour over the places of your story, then "The End", the **Finished the Journey** achievement and a **Your Story** book (about 15 to 20 pages, can't be copied).
* **Achievements**: a real Minecraft achievement (toast, chat line, Adventure tab) for every chapter and one for finishing the journey. They are created by the plugin at startup, so there is no datapack or resource pack to install. New chapters get one automatically. Players who earned one while it didn't exist yet (or after a restore) get it when they join.
* **B.O.B** is the server's Discord bot who somehow grew legs. He wants you to place 1000 dirt so he can touch grass.

## Anti abuse

* NPCs can't be hurt, pushed, traded with, converted or moved. They are never saved to the world.
* A protected area (`shield.radius`) stops building, breaking, buckets, explosions and PvP around villagers.
* NPCs placed with `/cq scatter` move to a new random spot in their area every 20 minutes, so nobody can camp them.
* Blocks you placed don't count for mining or harvesting, and placing the same spot twice doesn't count twice.
* Spawner and spawn egg mobs don't count for kill quests.
* Deliveries take the items before the quest counts; a quest is saved as done before rewards are given, so it can't be claimed twice.
* The quest menu can't be taken from, and the story book is given once.

## Saving and recovery

* Progress is saved the moment a quest is finished, every minute, when a player leaves and on shutdown.
* Saves are written to a temp file and swapped in, so a crash mid save can't corrupt a file. The previous version is kept as `players/<uuid>.yml.bak` and is used automatically if a file is ever damaged.
* Every 6 hours and on every shutdown all quest data is zipped into `plugins/CQuests/backups/` (the last 28 are kept).
* Something went wrong? `/cq backups` to see them, then `/cq restore latest Steve` for one player or `/cq restore latest all` for everyone. It works while players are online, and the files it replaces are kept as `.yml.before-restore`.

## Performance

* An NPC only exists while a player is within 100 blocks. 100 NPCs on an empty map cost nothing.
* Side quests are generated on demand from a seed and cached; the million quests are never stored.
* Player files save asynchronously. Everything runs on the right Folia region thread.

## Placing villagers

* Stand somewhere and run `/cq npc place stephan`.
* Or scatter a group: make a WorldGuard region (or `/cq pos1` and `/cq pos2`) and run `/cq scatter act1 spawn`. They spread out on solid ground and wander inside that area.
* Spots are saved in `plugins/CQuests/spawns.yml`.

## Files

| File | |
|---|---|
| `config.yml` | How it behaves: money command, ranges, shield, reward rules |
| `messages.yml` | Every text players see: prefix, name tags, villager chat, messages |
| `npcs.yml` | Every villager: name, title, profession, villager type, baby, player skin, lines |
| `quests.yml` | Chapters and the story quests |
| `generator.yml` | How side and daily quests are made, reward tiers and effects |
| `spawns.yml` | Where every NPC stands |
| `players/<uuid>.yml` | Each player's progress |

### Villager looks

In `npcs.yml` each villager has a `profession` (FARMER, LIBRARIAN, ...), a `skin` (PLAINS, DESERT, JUNGLE, SAVANNA, SNOW, SWAMP, TAIGA), and optionally:

```yaml
    baby: true              # a baby villager
    player-skin: "Notch"    # a player shaped NPC with that player's skin (Minecraft 1.21.9+)
```

On servers older than 1.21.9 player skin NPCs show as villagers.

### Adding chapter 6 and beyond

The story keeps going as long as there are quests. To add a chapter:

1. Add villagers to `npcs.yml` (give them `act: 2` and `personal: true` to only show them to players who need them).
2. Name the chapter in `quests.yml` under `chapters:`, for example `6: "The Long Winter"`.
3. Add story quests at the bottom of `quests:` with `chapter: 6`. Each one automatically follows the quest above it; add `side-required: 15` to set how many side quests it needs.
4. `/cq reload`. Players who finished chapter 5 continue straight into chapter 6. The ending plays after whatever quest is last.

Quest format:

```yaml
  story_rowan:
    name: "Into the Snow"
    level: 101
    giver: rowan
    chapter: 6
    side-required: 15
    big: true
    objectives:
      - "KILL STRAY 20 strays"
      - "DELIVER SNOWBALL 64 snowballs"
    description: "Help {npc:rowan} clear the pass."
    offer: ["The pass is full of strays."]
    complete: ["The road is open again!"]
    rewards:
      money: 3000
      items: ["DIAMOND 2"]
      effects: ["SPEED 3600 1"]
```

Objective types: `KILL`, `MINE`, `HARVEST`, `PLACE`, `CRAFT`, `SMELT`, `FISH`, `BREED`, `TAME`, `SHEAR`, `ENCHANT`, `CONSUME`, `DELIVER`, `TALK`. Targets take `A|B`, wildcards like `*_LOG`, groups like `@IRON` or `ANY`.

## Tested on

Every push builds the plugin, runs the unit tests and then starts real servers with it (Paper 1.21.4, the newest Paper and the newest Folia), places all NPCs, runs admin commands and `/cq reload`, and fails on any error. See `.github/scripts/smoke-test.sh`.

## Building

```
./gradlew build
```

Java 21. The jar ends up in `build/libs/`. The story files are generated by `tools/story` (see its README).
