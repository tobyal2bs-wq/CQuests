# CQuests

**Boss polish update 1.16.5:** connected joints, stable faces/turning, individual entrances, no aura rings, and 2,000/5,000 HP. [Friendly Mossback commands and update notes](RELEASE-1.16.5.md).

**Boss polish update 1.16.4:** connected joints, stable faces/turning, individual entrances, no aura rings, and 2,000/5,000 HP. [Friendly Mossback commands and update notes](RELEASE-1.16.4.md).

A villager quest plugin for Paper and Folia. Players follow a linked story told by villagers across up to ten chapters, take on side quests and daily quests, fight private bosses that only they can see, farm wheat for levels, trade with travelling merchants and get letters from the villagers they met. No resource pack or datapack is needed, and Bedrock players through Geyser get matching menus.

* **Story**: 101 story quests over chapters 1 to 5, plus chapters 6 to 10 (100 more villagers) that you switch on with `/cq chapter 6 on`. Each chapter costs money to start, and finishing chapter 5 gives an elytra.
* **Bosses**: private fights at the end of chapters 5 to 10 and mini bosses halfway through 6 to 10. Only the player sees them, they only hurt that player and they never break blocks. Pip can fight next to you with a bow or a sword in 3 boss fights.
* **Side, daily and co-op quests**: over a million generated side quests, a daily quest that differs for every player and pays a little or a lot, daily streaks, and co-op dailies for 2 to 4 friends working at the same time.
* **World bosses and boss spots**: 25 public bosses, 4 legends (the Warden, Wither, Ender Dragon and Breeze bosses) and 12 seasonal ones (three per season), each a hand-built block model of 150+ blocks with its own entrance, attacks and death. One wakes every week, and any arena can be a spot that wakes a different boss on its own timer (every 2h, every 400h, anything). You draw a border they can never cross and no-pass areas they can never enter. They attack any player, never break blocks, and their shockwaves and falling meteors are block effects that leave no trace.
* **Seasons, tutorial and invites**: Halloween, Winterfest, Spring and Summer events you switch on with a command, a first quest that pays out within minutes, and rewards for inviting friends.
* **Finding your way**: every player's compass points to their next villager, with an arrow and distance above the hotbar and `/quests where`.
* **Villagers know your server**: tips for how an item is crafted, smelted or mined come from the server's own recipes, so new blocks and items on newer Minecraft versions just work.
* **Extras**: Discord announcements, PlaceholderAPI placeholders for everything, renaming every NPC, WorldGuard farms, backups, and `/cq test` for every feature.

Release notes for every version are in [CHANGELOG.md](CHANGELOG.md).

A villager quest plugin targeting **Paper 1.21.4 through 26.2 and compatible forks**, with region schedulers for Folia and compatible views for Bedrock/Geyser. The exact tested builds are recorded in [VALIDATION-1.2.md](VALIDATION-1.2.md); arbitrary engines and versions are not universally guaranteed.

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
| `/cq test boss <quest>`, `bossphase`, `bossstop`, `bossevent <event>`, `all` | op | Start any boss fight next to you and watch it (nothing counts) |
| `/cq test discord <event>` | op | Send a sample Discord post |
| `/quests where` | `quests.use` | Who to visit next, how far and which way |
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

1.7.0 ships five more chapters, with 20 villagers each since 1.8.0 (a mini boss halfway, a boss at the end): 6 The Iron Tusk, 7 Tides of the Drowned, 8 The Ember Court, 9 The Bone Choir and 10 The Listener Below. They are **off** until you switch them on, so you can try them first:

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

### World bosses

One world boss wakes every week (`world-bosses.schedule`, Saturday 20:00 by default) at the arena called `main`.

1. Stand where it should appear and run `/cq worldboss setspawn main`.
2. Run `/cq worldboss wand main` and left-click blocks around the arena to draw its border, corner by corner. Right-click removes the last corner, sneak + right-click shows the border. Without a border the boss stays inside a circle (`/cq worldboss radius main 40`).
3. `/cq worldboss next` shows which boss comes next and when. `/cq worldboss spawn <boss>` starts one now, `/cq worldboss stop` sends it away.

#### Boss spots

Any arena can wake bosses on its own timer, separate from the weekly boss:

- `/cq worldboss interval <arena> 2h` (or `400h`, `90m`, `1d12h`, `off`). Each time a different boss wakes, and each fight picks its own patrol pattern (orbit, figure eight, zigzag, wander or star), turning direction, size and speed, so no two fights move alike.
- `/cq worldboss nopass <arena> here [radius]` adds a circle the boss can never enter; `corner` (run it at two opposite corners) adds a box. `list`, `remove <n>`, `clear` and `show` manage them. Minions are kept out too.
- `/cq worldboss spots` lists every spot, its next boss time and its no-pass areas. Options are under `world-bosses.spots` in `config.yml`.

Controlling bosses (every `/cq worldboss` and `/cq test worldboss` command, the boss panel and the border stick) is for operators and anyone with the `bosses.use` permission, the same permission CBosses uses.

A world boss only attacks players, is pulled back the moment it reaches its border, never breaks, burns or changes blocks, drops nothing and is never saved into the world. Players have to stand inside the border to hurt it. Everyone who did at least 2% of its health is paid; the top 3 get more. Bosses, their looks, attacks and rewards are in `worldbosses.yml`. Try any of them with `/cq test worldboss <id>` or go through all of them with `/cq test worldbossnext`. Players see the next one with `/quests worldboss`.

Each boss is drawn as a jointed model built from display blocks that rides the invisible mob, with its own entrance, at least three attack animations and its own death. Hits land where you aim: weak spot x2.5, head x1.5, arms and tail x0.8, armour x0.6, the weapon x0.3. `world-bosses.models: false` in `config.yml` turns the models off; `model: none` on one boss turns it off for that boss.

### Seasons

`/cq season` lists Halloween, Winterfest, Spring Bloom and Summer Blaze. `/cq season halloween on` starts one now, `off` ends it, `auto` runs it between its dates every year. While a season is on, its daily quests can be offered and its world boss takes the weekly slot.

### Tutorial and invites

The tutorial quest "First Steps" starts right after the welcome quest and pays out within a few minutes (`quests.tutorial-quest`). New players type `/quests invitedby <name>` in their first 48 hours: they are paid at once and the friend who invited them is paid when they finish the tutorial (`invites` in config.yml). Players on the same connection don't count.

### Daily streaks

Finishing the daily on the day after the last one adds a day to the streak. Each day adds `daily.streak-bonus-percent` (10%) of the daily's money, up to `daily.streak-max-days` (7). A missed day starts again at 1. Turn it off with `daily.streaks: false`.

### Discord

Paste a webhook link into `discord.webhook-url` and `/cq reload`. CQuests posts when someone finishes a chapter, finishes the journey, beats a boss or reaches a 7, 30 or 100 day streak. Each event can be turned off or reworded under `discord.events` and `discord.messages`. Posts are sent in the background (never on the server thread), at most one every 2 seconds, and can never ping `@everyone`, roles or users.

### Placeholders

Server-wide: `worldboss_next` (time left), `worldboss_next_name`, `worldboss_alive`, `season` (seasons running now). Per player: `invites`.

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
