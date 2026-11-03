# CQuests 1.8.0

Bigger chapters 6 to 10, mini bosses, chapters that cost money, test commands for every boss, and players can always find their next villager. All progress carries over.

## Upgrading

1. `/cq backup`, stop the server, replace the jar, start it.
2. The new villagers, quests and bosses are added to your `npcs.yml`, `quests.yml` and `bosses.yml` (backups are saved as `*.before-1.8.0`). Your own text edits are kept. Only the order of the chapter 6 to 10 story quests is updated, so the new quests fit in.
3. Chapters 6 to 10 are still off until you run `/cq chapter 6 on` and so on.

## Chapters 6 to 10: 20 villagers each

Every chapter now has 20 villagers and 20 story quests, like chapters 1 to 5. That's 100 villagers and 100 quests in total, and each new villager also has its own generated side quests. Halfway through every chapter there is now a **private mini boss**:

| Chapter | Mini boss | Final boss |
|---|---|---|
| 6 The Iron Tusk | Sergeant Ironjaw (Vindicator with Pillagers) | Gorehorn (Ravager) |
| 7 Tides of the Drowned | Old Frostpaw (Polar Bear) | Queen Brinewyn (Drowned) |
| 8 The Ember Court | Goldtooth's Enforcer (Piglin Brute) | Pyra (Blaze) |
| 9 The Bone Choir | The Frost Cantor (Stray with Skeletons) | Sir Mortis (Wither Skeleton) |
| 10 The Listener Below | The Echo Wind (Breeze) | The Listener Below (Warden) |

Mini bosses follow the same rules as the big ones: only you see them, they only hurt you, they never break blocks, they drop nothing and they are never saved to the world. No quest asks for wheat.

## Chapters cost money

Starting a chapter (taking its first story quest) costs money through Vault: 25k for chapter 2, then 50k, 100k, 250k, 500k, 750k, 1M, 1.5M and 2.5M for chapter 10 (since 1.8.1). If the player can't pay, the villager says how much it costs and nothing is taken. If the quest can't start, the money is refunded. Change the prices under `chapters.cost` in `config.yml`, or turn them off with `chapters.costs-enabled: false`. Without Vault and an economy plugin, chapters stay free.

## Test everything

| Command | What you see |
|---|---|
| `/cq test all` | Every boss, clickable |
| `/cq test boss <quest>` | That boss fight starts next to you, in any game mode. Nothing counts and nothing drops. In creative you can watch without being hurt |
| `/cq test bossphase` | Jumps your test boss to half health, so you see it get angry, call its minions and use its events |
| `/cq test bossstop` | Ends the fight |
| `/cq test bossevent <lightning, darkness, slowness, levitate or roar>` | Plays one boss event on you |
| `/cq test discord <chapter, boss, streak or journey>` | Sends a sample post to your Discord webhook |
| `/cq test where` | Shows what players see when they ask for their next villager |

The older test commands still work: `/cq test celebrate`, `chapter <n>`, `ending`, `welcome`, `achievement` and `book`.

## Finding villagers

* **Every player's compass points to their next villager.** No special item is needed, and it updates when the quest changes.
* **The arrow and distance above the hotbar are on by default** for new players. `/quests directions` turns them off. On servers updating from an older version, set `directions.default-on: true` in `config.yml` to turn it on for everyone who hasn't changed it.
* **`/quests where`** says who to visit next, how far away they are, which direction (north-east and so on) and their coordinates.
* **New players are told where villager number one is** a few seconds after the welcome message.

## Farm

* The farm hint no longer switches your hotbar slot to the hoe by itself.

## Performance

* The compass is only updated when its target changes, at most once every 2 seconds per player. Its cache is cleared on logout.
* Test bosses use the same capped, region-safe fight code as real ones.

Tested on Paper 1.21.4, the newest Paper and the newest Folia: the test player asks `/quests where`, starts a test boss, jumps it to half health and stops it. The JAR attached to the release is the exact file built and tested in that run.
