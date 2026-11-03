# CQuests 1.7.0

Five new chapters with private boss fights, Discord announcements, daily streaks, world-wide scattering, a placeholder for every value, and no more wheat quests. Everything new that changes the story is **off until you switch it on**, so you can try it before your players see it. All player progress carries over.

## Upgrading from 1.6.6

1. Run `/cq backup` (or copy `plugins/CQuests/`).
2. Stop the server, replace the jar with `CQuests-1.7.0.jar`, start the server.
3. On first start CQuests adds the new villagers and quests to your `npcs.yml` and `quests.yml` (backups are written as `*.before-1.7.0`) and creates `bosses.yml`. Your own edits stay. New config keys use their defaults until you add them; see the new sections at the bottom of the bundled `config.yml`.

## Chapters 6 to 10 (off by default)

| Chapter | Name | Boss |
|---|---|---|
| 6 | The Iron Tusk | Garrick's Ravager, with Vindicators |
| 7 | Tides of the Drowned | Brine's Drowned captain with a trident, with Drowned |
| 8 | The Ember Court | Emberly's Blaze, with Blazes |
| 9 | The Bone Choir | Mortimer's Wither Skeleton with a netherite sword, with Skeletons |
| 10 | The Listener Below | Elder Aldis's Warden |

* 50 new villagers (10 per chapter) and 50 new story quests, each chapter ending in a boss fight. Chapter 5 already ends with the Wither.
* `/cq chapter` lists every chapter and whether it is on. `/cq chapter 6 on` turns chapter 6 on for everyone; `/cq chapter 6 off` hides it again. Works from the console.
* While a chapter is off its villagers do not spawn and its quests do not exist, so players stop at the last chapter that is on. Turning it on lets players who finished chapter 5 carry straight on. Turning it off never deletes progress.
* Level gates for chapters 6 to 10: 420, 440, 460, 480 and 500 (`progression.chapter-levels`).

## Bosses

Bosses are configured in `bosses.yml` (mob type, health, weapon, minions, events). Every boss and its minions:

* are visible only to the player who called them; nobody else sees, hits or gets hit by them
* only target and damage their owner, and can only be damaged by their owner
* **never break blocks**: explosions, fireballs, fire, trampling and griefing are cancelled; undead do not burn in daylight
* drop nothing and are never saved into the world, so a crash or restart leaves nothing behind
* leave if the player dies, logs out, walks more than 48 blocks away or takes longer than 10 minutes, and the player can try again
* trigger events at half health and every 20 seconds after: harmless lightning around the player, darkness, slowness, a short levitation or a roar, plus minions at half health
* only count the boss kill for the boss quest; killing another Ravager or Warden does not complete it

Performance: one light timer per active fight on the boss's own region thread (Folia safe), a boss bar per fight, and `max-active` (6) fights on the whole server at once. No server-wide listeners are added.

## Discord webhook

Set `discord.webhook-url` and run `/cq reload`. CQuests posts when a player finishes a chapter, finishes the whole journey, beats a boss, or reaches a 7, 30 or 100 day daily streak (and every full year). Each event can be switched off or reworded under `discord.events` and `discord.messages`.

* Sent on one background thread, never the server thread; at most one post every 2 seconds and at most 64 waiting.
* Mentions are disabled and names are escaped, so a player called `@everyone` or `**bold**` cannot ping or break the message.
* Only real Discord webhook links are accepted.

## Daily streaks

Finishing the daily on the day after the last one adds one to the streak. Each streak day adds 10% of the daily's money as a bonus, up to 7 days (+60%). Missing a day starts again at 1. Keys: `daily.streaks`, `daily.streak-max-days`, `daily.streak-bonus-percent`; message `daily-streak` in `messages.yml`.

## World scatter

`/cq scatterworld <chapter6|act1|act2|all|ids> <size|border> [depth] [world] [centerX centerZ]` now spreads villagers over the world itself: a square of that size around the world border centre (normally 0, 0), not around you or spawn. `border` uses the whole world border (capped at 100,000). Only safe ground is used and progress never changes. Example: `/cq scatterworld chapter6 10000`.

## No wheat quests

No quest asks for wheat any more:

* "Steve's" story quest now asks for 16 carrots, potatoes or beetroots.
* "Mabel's" story quest now asks you to shear 6 sheep.
* Generated side and daily quests use carrots instead of wheat.

Players who already have one of these quests active keep their current progress; the new objective applies when the quest is next loaded.

## Placeholders

With PlaceholderAPI every value is available as `%cquests_<name>%`, and any number can end in `_formatted` (`1,234,567`) or `_short` (`1.2M`). The full list is in the README under "Placeholders": level and XP with a progress bar, story progress and percent, current chapter and its name, next story quest and villager, completed, side and daily counts, daily streak, daily ready and cooldown, active quest name, villager, progress and objective, and more. Placeholders only read data already in memory, so they are safe for scoreboards and tab lists on Folia.

## Compatibility

* Paper 1.21.4 and newer, Folia, and Paper or Folia forks. Version-specific names (attributes, sounds) are looked up at runtime, so a missing one is skipped instead of crashing.
* New code holds no player or entity references after a fight ends, and everything is cleaned up on logout, reload and shutdown.

## Tested

* Unit tests for locked chapters, loading all ten chapters cleanly, every boss pointing at a real quest, no wheat anywhere, daily streaks across restarts, Discord escaping and number formatting.
* GitHub Actions starts real Paper 1.21.4, newest Paper and newest Folia servers. The console lists chapters and switches chapter 6 on and off again. Any CQuests error or warning fails the run.
* The JAR attached to the release is the exact file built and tested in that run.
