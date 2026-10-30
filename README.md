# CQuests

A villager quest system for Paper and Folia (and forks like Leaf), Minecraft 1.21.4 and newer.

- **100 linked lore villagers.** 15 stand at spawn: 14 story villagers (Stephan, Jerry, Steve, B.O.B...) plus the daily villager. The other 86 live out in the world, ending with the Wither fight in "The King Wakes" and the trip home in "A New Dawn". Each one gives a story quest, and each quest is a bit harder than the one before it.
- **1,000,000 side quests**, 10,000 per story villager, generated on demand from templates in `generator.yml`, so the number costs no memory. They mix one to three objectives and get bigger and harder the further you go. A villager's side quests unlock once you finish their story quest.
- **A long story.** Before the next villager's chapter opens, you do 10 side quests for the current one (`side-quests-per-chapter`). That makes the main story about 1,100 quests, which is weeks of play.
- **Celebrations and an ending.** Big chapters end with a title, fireworks and sounds. The last quest plays an in-game replay: the camera flies over the places where your story happened, shows your stats and "The End", then gives the custom advancement **Finished the Journey** and announces it to the server. Admins can preview it with `/cq finale`.
- **A daily villager** (Granny Marigold) hands out one job every 24 hours for 10k.
- **A quest journal book** (`/quests`) laid out like the reference screenshots: one page per active quest (title, level, status, objectives with progress, `« All quests`), the "All Quests" index with a progress bar and ✔ / ○ / ✖ per quest, then side quests and the daily.
- **Click dialogue.** Villagers introduce themselves the first time you click them, tell you what they need, take deliveries out of your inventory and pay you on turn-in.
- **Simple rewards.** Money goes through `/eco give %player% <amount>` and items are plain vanilla items. Only the hardest quests give rare items.

## Installing

1. Drop `CQuests-<version>.jar` into `plugins/`. WorldGuard, Geyser and Floodgate are optional.
2. Start the server once. Any villager without a spawn point is placed around the world spawn automatically (act 1 close in, act 2 further out), and the positions are saved to `plugins/CQuests/spawns.yml`.
3. Move the villagers to where you want them (see below) and `/cq reload` after editing files.

Building from source needs JDK 21: `./gradlew build`. The jar ends up in `build/libs/`.

## Placing villagers

| Command | What it does |
| --- | --- |
| `/cq npc place <id>` | Stand somewhere and put that villager there (facing the way you face). |
| `/cq npc remove <id>` | Take a villager off the map. |
| `/cq npc tp <id>` | Teleport to a villager. |
| `/cq npc list` | All villager ids. Green ones are placed, red ones are not. |
| `/cq scatter <ids\|act1\|act2\|all> <worldguard-region> [world]` | Spread villagers at random spots on solid ground inside a WorldGuard region. |
| `/cq pos1`, `/cq pos2`, then `/cq scatter <...>` | The same, inside a box you select yourself. |

`<ids>` is a comma-separated list such as `jerry,steve,bob`, so you can scatter 10 or more villagers in one region at once.

Villagers spawn even inside WorldGuard regions that deny mob spawning: the plugin tags its own villagers and lifts any cancel on them. They are invulnerable, can't be pushed, don't trade, and are re-created automatically if they ever go missing.

Act 2 villagers are **personal**. A player only sees one when they have a quest that involves it, when it's their next story stop, or after they've met it. Set `personal: true` on any villager in `npcs.yml` to get the same behaviour, for example a villager that only appears to the player who has to bring it items.

## Players

| Command | What it does |
| --- | --- |
| `/quests` | Open the quest journal. |
| `/quests list` | The same information in chat. |
| `/quests accept` | Accept the offer a villager just made. This is the same as clicking the villager again. |
| `/quests abandon <id>` | Drop a side or daily quest. Story quests can't be abandoned. |

## Admin

`/cq reload`, `/cq quest <id>`, `/cq finale [player]` (preview the ending; no advancement) and `/cq player <name> reset | complete <quest> | give <quest> | resetdaily`. Permission: `cquests.admin` (op by default).

## Files

- `config.yml`: money command, chat formats, daily settings, spawn rings, journal layout, target groups and messages.
- `npcs.yml`: the villagers (name, title, profession, skin, level, act, intro and idle lines).
- `quests.yml`: the welcome quest and the 100 story quests. Objective lines look like `KILL WOLF 3 wolves`, `DELIVER WHEAT 16 wheat`, `MINE @IRON 24 iron ore` or `TALK jerry`. The file header lists every type.
- `generator.yml`: templates for side quests and the daily pool. `side-quests-per-npc: 10000` across 100 story villagers gives 1,000,000 quests. Add targets, names or places there to get more variety.
- `players/<uuid>.yml`: each player's progress. Side quests are stored as a count per villager, so files stay small.

The "Finished the Journey" advancement sits in the Adventure tab. It is loaded into the server at startup. If a server version refuses that, a datapack is written to `<world>/datapacks/cquests` instead and loads after the next restart.

Objective types: KILL, MINE, HARVEST (fully grown crops only), PLACE, CRAFT, SMELT, FISH, BREED, TAME, SHEAR, ENCHANT, CONSUME, DELIVER, TALK. By default, breaking a block you placed yourself doesn't count towards MINE.

## Bedrock players

Everything works through Geyser. The journal is a plain written book with no Java-only widgets. Bedrock players turn pages instead of clicking the page links. The chat `[Accept]` button is hidden for them and they accept by clicking the villager a second time. Floodgate is detected automatically when it is installed.
