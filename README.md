CQuests **1.7.2** fixes the wheat farm: inside a saved field only the farm hoe harvests, new players get the free hoe automatically, and the action bar explains what to do. See [RELEASE-1.7.2.md](RELEASE-1.7.2.md).

CQuests **1.7.1** gives the Discord posts a proper embed: player face and skin, title, fields, a story progress bar and a footer. See [RELEASE-1.7.1.md](RELEASE-1.7.1.md).

CQuests **1.7.0** adds chapters 6 to 10 (50 new villagers, each chapter ending in a private boss fight), switched off until you run `/cq chapter 6 on`. It also adds Discord webhook announcements, daily quest streaks, `/cq scatterworld` across the whole world, a PlaceholderAPI placeholder for every number and name, and removes wheat from every quest. See [RELEASE-1.7.0.md](RELEASE-1.7.0.md).

CQuests **1.6.6** is a stability and performance release: NPCs under roofs or trees spawn again, a server-wide mob movement listener is gone, offline players leave memory, and renaming an NPC now changes its name everywhere (quest text, tracker, directions, mail, menus) and works from the console. See [RELEASE-1.6.6.md](RELEASE-1.6.6.md).

CQuests **1.3.3** separates and lifts NPC nameplates above private speech, improves name/level contrast and adds slower typing with a reading pause for every sentence. See [validation](AUDIT-1.3.3.md) and [farm testing](FARM-TESTING.md).

CQuests **1.3.2** adds `/cq merchant test [id|stop]`: a private temporary walk and trade preview that does not spend items or money or alter saved merchants. See [setup](MERCHANTS-1.3.md) and [validation](AUDIT-1.3.2.md).

CQuests **1.3.1** simplifies merchant setup to spawn, wand trail, then end (including final facing), adds an OP skin command for quest NPCs, and bounds queued GUI callbacks during packet bursts. See [merchant setup](MERCHANTS-1.3.md) and [validation](AUDIT-1.3.1.md).

# CQuests

Version 1.3 adds five travelling merchant presets, operator-only route and trade editing, item/money/mixed trades, and additive story twists. See [MERCHANTS-1.3.md](MERCHANTS-1.3.md) for placement, GUI controls and security boundaries.

Version 1.2.3 closes an offhand farm-container bypass, preserves placed-block quest protection through piston movement, and prevents conversation chat loss during buffer overflow or conversation completion. It includes the previous reconnect/save, personal-tool and client compatibility fixes. See [AUDIT-1.2.3.md](AUDIT-1.2.3.md) and [AUDIT-1.2.2.md](AUDIT-1.2.2.md) for validation and remaining limits.

A villager quest plugin targeting **Paper 1.21.4 through 26.2 and compatible forks**, with region schedulers for Folia and compatible views for Bedrock/Geyser. The exact tested builds are recorded in [VALIDATION-1.2.md](VALIDATION-1.2.md); arbitrary engines and versions are not universally guaranteed.

100 story villagers tell Claude's original linked story over 5 chapters, with 8 additional side-job villagers and one daily villager. There are 1,080,000 generated side quests. Original story IDs, generator seed and player progress are preserved. No resource pack or datapack is needed.

Version 1.2 adds private letter-by-letter NPC speech, native Minecraft dialog choices on capable servers, a paginated book journal, custom levels, personal wheat tools, anvil upgrades and exact WorldGuard-bound polygon farms. One click harvests one mature wheat and fully regrows it after one second. Tool unlocks return to a personal locker outside the farm. Chapter broadcasts and new farming/level achievements reward progress. The boss bar, direction arrow/meters and mandatory side-job quotas remain off by default. See [INSTALL-1.2.md](INSTALL-1.2.md) for setup, preservation, pacing and rollback.

## Install

1. Download `CQuests-<version>.jar` from the latest build (GitHub Actions, "Build" workflow, artifact) and put it in `plugins/`.
2. Quest rewards default to `/economy give`. Paid farm upgrades require Vault and your economy's registered Vault provider. Change `money-command` if your reward command differs.
3. Start the server. Five camp residents plus the daily villager are placed around spawn on validated terrain, the rest further out. Existing positions are preserved; `/cq camp` explicitly arranges this layout. Failed searches retain old positions.
4. Give players the quest command: `/lp group default permission set quests.use true`
5. Optional: move the villagers to your own spots (see "Placing villagers").

WorldGuard is required for farming, alongside its matching WorldEdit dependency. PlaceholderAPI enables `%cquests_level%` and every other number and name (see "Placeholders"). These integrations are optional for ordinary quests. NPCs can spawn inside regions with `mob-spawning deny`.

## Commands

| Command | Who | What it does |
|---|---|---|
| `/quests` | `quests.use` | Journal in your saved book, menu or chat mode |
| `/quests book` | `quests.use` | The journal book with every quest and the "All Quests" pages |
| `/quests list` | `quests.use` | Active quests in chat |
| `/quests farm` | `quests.use` | Personal field workshop and hoe locker |
| `/cq farm wand <id>` / `/cq farm outside <id>` | op | Select an inside/inverse polygon; save with `/cq farm save <id> <wg-region>` |
| `/cq farm anvil` | op | Bind the anvil you are looking at to the upgrader |
| `/cq camp` | op | Arrange five spawn residents plus the daily villager without resetting progress |
| `/quests track` | `quests.use` | Turn the boss bar tracker on or off |
| `/quests story` | `quests.use` | Read your story book again after finishing the journey |
| `/quests abandon <quest>` | `quests.use` | Drop a side or daily quest |
| `/cq reload` | op | Reload config, NPCs and quests |
| `/cq npc list` | op | All NPCs and where they stand |
| `/cq npc place <id>` | op | Put an NPC where you stand |
| `/cq npc remove <id>` | op | Take an NPC off the map |
| `/cq npc tp <id>` | op | Teleport to an NPC |
| `/cq npc rename <id> <name>` | op or console | Rename an NPC everywhere. Colours work (`<gold>Jerry`). Progress is unchanged |
| `/cq character <id> name\|title\|prefix\|intro\|idle <text>` | op or console | Change any quest NPC, merchant or Pip: name, title, name tag prefix, first-meeting lines, idle lines |
| `/cq character <id> reset` | op or console | Undo every change for that character |
| `/cq pos1`, `/cq pos2` | op | Select a box to scatter NPCs in |
| `/cq scatter <ids, act1, act2 or all> [region] [world]` | op | Spread NPCs in a WorldGuard region or your box. They keep wandering inside it |
| `/cq scatterworld <chapter6, act1, all or ids> <size or border> [depth] [world] [centerX centerZ]` | op | Spread NPCs over the whole world (a square of that size around the world border centre), not around you |
| `/cq chapter [number] [on\|off]` | op or console | List chapters, or switch one on or off for everyone. Chapters 6 to 10 start off |
| `/cq player <name> reset` | op | Wipe a player's quest progress |
| `/cq player <name> complete <quest>` | op | Mark a quest done |
| `/cq player <name> give <quest>` | op | Give a quest |
| `/cq player <name> resetdaily` | op | Let a player do the daily again now |
| `/cq quest <id>` | op | Show a quest's details |
| `/cq finale [player]` | op | Preview the ending (no rewards) |
| `/cq test messages` | op | Show every message from messages.yml with sample values |
| `/cq test welcome` | op | Show the new player guide |
| `/cq test celebrate` | op | Play the big quest animation on you |
| `/cq test chapter <number>` | op | Play a chapter complete animation on you |
| `/cq test ending` | op | Play the ending cinematic (no rewards) |
| `/cq test achievement <chapter, end or reset>` | op | Give yourself an achievement, or take them all back |
| `/cq test finish <npc>` | op | Act as if you finished a villager, so it disappears for you |
| `/cq test unfinish <npc>` | op | Undo that exactly; the villager comes back |
| `/cq test roam <npc>` | op | Move a scattered villager to a new spot now |
| `/cq test book` | op | Read your "Your Story" book as it is so far |
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
2. Click a villager with a white name, read the dialogue, then choose your response.
3. Your book journal shows the next step. Enable the boss bar or arrow directions in /quests settings if you want them.
4. Follow the story at your pace. Side jobs are optional by default and reward continued exploration.

## How it plays

* **Click a villager** to read a paginated conversation. Choose Accept quest or Claim rewards. Use /quests mode menu for chest dialogue, or /quests mode chat for the original timed speech.
* **The story** remains 101 quests in 5 chapters, with the original IDs and objectives. Side-job quotas are optional: quests.require-side-quests is false by default.
* **Side quests** are generated from `generator.yml`: kill, mine, harvest, fish, breed, tame, shear, craft, smelt, enchant, eat, deliver and place quests, getting harder and paying more as you go. Bigger quests pay more.
* **Daily quest**: Marigold gives one job every 24 hours for 10,000.
* **Rewards** are money plus normal items. No elytra, dragon eggs, god apples, totems, beacons or nether stars. Netherite only from level 85 quests. Some side quests give a potion effect like 1 hour of Swiftness.
* **Chapter visibility** hides future villagers until their first chapter. Shared NPCs unlock at their earliest involvement. Earlier villagers remain available for optional side work.
* **Animations**: big quests and chapter ends play a particle helix, a typed out title, music and fireworks, then the next chapter card. The last quest plays a camera tour over the places of your story, then "The End", the **Finished the Journey** achievement and a **Your Story** book (about 15 to 20 pages, can't be copied).
* **Achievements** include a separate Wanderers tab, chapter and ending goals, plus 14 side-job, daily and exploration milestones. Existing counters grant earned milestones on join.
* **B.O.B** is the server's Discord bot who somehow grew legs. He wants you to place 1000 dirt so he can touch grass.

## Anti abuse

* NPCs can't be hurt, pushed, traded with, converted or moved. They are never saved to the world.
* A protected area (`shield.radius`) stops building, breaking, buckets, explosions and PvP around villagers.
* NPCs placed with /cq scatter or /cq scatterworld stay in their saved positions by default. Set spawning.roam-minutes above zero for optional roaming.
* Blocks you placed don't count for mining or harvesting, and placing the same spot twice doesn't count twice.
* Spawner and spawn egg mobs don't count for kill quests.
* Deliveries take items before progress is counted. Completed quests and one-use conversation responses reject duplicate click claims; progress is saved asynchronously.
* The quest menu can't be taken from, and the story book is given once.

## Saving and recovery

* Progress is queued for saving when a quest finishes, every minute, when a player leaves and on shutdown.
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

### Renaming NPCs and merchants

Every quest NPC, every merchant and Pip the companion can be renamed in game or from the console, without touching the YAML files or anyone's progress:

```
/cq npc rename jerry Farmer Jerold
/cq npc rename bob <aqua>B.O.B 2.0
/cq character flora name Flora the Seed Seller
/cq character stephan title Keeper of Dawn
/cq character stephan intro Hello there, {player}! | Welcome to the camp.
/cq character jerry reset
```

* The new name shows everywhere: name tags, speech, `{npc:id}` mentions in quest text, the boss bar, directions, the journal, mail and letters, menus and admin messages.
* Commands still accept the id (`jerry`) or the shown name with dots and spaces ignored (`b.o.b`, `farmerjerold`).
* Changes are saved in `plugins/CQuests/characters.yml` and survive restarts and `/cq reload`. Ids, quests and player progress are never rewritten.
* `/cq npc list` shows each id with its current name next to it.
* Lines written inside `quests.yml` (offers and completion lines) are your own text, so a villager's old name there stays until you edit it.

### Chapters 6 to 10 and bosses

1.7.0 ships five more chapters with 10 villagers each: 6 The Iron Tusk, 7 Tides of the Drowned, 8 The Ember Court, 9 The Bone Choir and 10 The Listener Below. They are **off** until you switch them on, so you can try them first:

* `/cq chapter` lists every chapter and whether it is on. `/cq chapter 6 on` switches chapter 6 on for everyone, `/cq chapter 6 off` hides it again. This writes `chapters.locked` in `config.yml` and reloads.
* While a chapter is off its villagers do not spawn and its quests do not exist. Players who already finished chapter 5 continue into chapter 6 as soon as it is on. Progress in a chapter you switch off is kept.
* `/cq scatterworld chapter6 10000` spreads the chapter's villagers over 10,000 × 10,000 blocks around the world border centre (`border` uses the whole border).
* Level gates for chapters 6 to 10 are 420 to 500 (`progression.chapter-levels`).

The last quest of chapters 5 to 10 is a boss fight, set up in `bosses.yml`: the Wither, a Ravager, a Drowned captain, a Blaze, a Wither Skeleton and a Warden. Every boss and its minions:

* are seen only by the player who called them, and only hurt and are only hurt by that player
* never break, burn or blow up blocks, drop nothing and are never saved to the world
* leave when the player dies, logs out, walks 48 blocks away or takes more than 10 minutes
* use events at half health and every 20 seconds after (harmless lightning, darkness, slowness, levitation, a roar), and call minions at half health
* are capped at `max-active` fights on the whole server (6 by default) and run on the boss's own region thread on Folia

### Daily streaks

Finishing the daily on the day after the last one adds a day to the streak. Each day adds `daily.streak-bonus-percent` (10%) of the daily's money, up to `daily.streak-max-days` (7). A missed day starts again at 1. Turn it off with `daily.streaks: false`.

### Discord

Paste a webhook link into `discord.webhook-url` and `/cq reload`. CQuests posts when someone finishes a chapter, finishes the journey, beats a boss or reaches a 7, 30 or 100 day streak. Each event can be turned off or reworded under `discord.events` and `discord.messages`. Posts are sent in the background (never on the server thread), at most one every 2 seconds, and can never ping `@everyone`, roles or users.

### Placeholders

With PlaceholderAPI installed every value is `%cquests_<name>%`. Add `_formatted` to any number for `1,234,567` or `_short` for `1.2M`, e.g. `%cquests_xp_formatted%`. Placeholders only read what is already in memory, so they are safe for scoreboards and tab lists on Folia.

| Numbers | Text |
|---|---|
| `level`, `xp`, `xp_required`, `xp_progress` (%) | `xp_bar`, `story_bar` (■■■■□□□□□□) |
| `story_done`, `story_total`, `story_percent` | `chapter_name`, `next_story`, `next_story_npc` |
| `chapter`, `chapters` | `story_finished` (yes/no) |
| `quests_completed`, `side_done`, `npcs_met` | `active_name`, `active_npc`, `active_category` |
| `dailies_done`, `daily_streak` | `active_progress` (3/10), `active_objective` |
| `active`, `active_story`, `active_side`, `active_daily`, `active_progress_percent` | `daily_ready` (yes/no), `daily_cooldown` (3h 20m) |
| `sunflowers`, `wheat`, `hoe_tier` | `bosses_enabled` (yes/no) |

### Adding chapter 11 and beyond

The story keeps going as long as there are quests. To add a chapter:

1. Add villagers to `npcs.yml` (give them `act: 2` and `personal: true` to only show them to players who need them, and `chapter: 11` so `/cq chapter 11 off` hides them).
2. Name the chapter in `quests.yml` under `chapters:`, for example `11: "The Long Winter"`.
3. Add story quests at the bottom of `quests:` with `chapter: 11`. Each one automatically follows the quest above it; add `side-required: 15` to set how many side quests it needs.
4. `/cq reload`. Players who finished the last chapter continue straight into the new one. The ending plays after whatever quest is last.

Quest format:

```yaml
  story_rowan:
    name: "Into the Snow"
    level: 101
    giver: rowan
    chapter: 11
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

The CI workflow builds the plugin, runs unit tests and boots isolated Paper/Folia servers. The legacy client suite checks book UI, opt-in tracking, directions, chapter hiding, menu actions and repeated scattering with animated speech and level gates disabled in its test fixture. See [VALIDATION-1.2.md](VALIDATION-1.2.md) for native dialogue, farming and integration coverage. Graphical client rendering and your custom economy still require staging checks.

## Building

```
./gradlew build
```

Java 21. The jar ends up in `build/libs/`. The story files are generated by `tools/story` (see its README).
