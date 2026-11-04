# CQuests 1.10.0

Weekly world bosses, seasonal events, a quick tutorial quest and rewards for inviting friends. All player progress carries over.

## Upgrading

1. Run `/cq backup`.
2. Replace the jar with `CQuests-1.10.0.jar` and restart. The tutorial and seasonal quests are added to `quests.yml` (backup `quests.yml.before-1.10.0`) and `worldbosses.yml` is created. New config keys use the bundled defaults until you add them to your `config.yml`.

## Weekly world bosses

20 public bosses, each a different mob, plus 4 seasonal ones. One wakes every Saturday at 20:00 (`world-bosses.schedule`: days, time, time zone, warning, rotate or random), with a chat warning 10 minutes before.

| Boss | Mob | Boss | Mob |
|---|---|---|---|
| The Gravelord | Wither skeleton | The Molten Colossus | Iron golem |
| The Broodmother | Spider | Jarl Hrimfrost | Stray |
| Warlord Gruk | Piglin brute | The Tide Tyrant | Drowned |
| The Storm Herald | Evoker | The Ironhide Behemoth | Ravager with a pillager rider |
| Bloodtusk | Hoglin | The Cinder Sovereign | Blaze |
| The Volatile Colossus | Charged creeper | King Gloop | Giant slime |
| The Executioner | Vindicator | Pharaoh Ankhamun | Husk |
| Ruinmaw | Zoglin | Hexmother Morwen | Witch |
| The Void Walker | Enderman | Fenrir | Wolf |
| Tempest | Breeze | The Pale Watcher | Creaking |

Seasonal: The Headless Horseman on a skeleton horse (Halloween), Old Man Winter (Winterfest), The Killer Bunny (Spring Bloom), Sunscorch (Summer Blaze).

Every boss is up to 4 times normal size, glows, wears glinting gear, has its own particle aura and ring, a boss bar showing its health, rage at half health and a set of attacks: lightning, shockwave, minions, fire ring, pull, leap, poison, blink, frost, arrow volley, darkness, levitate, heal, quake, detonate and roar.

* `/cq worldboss setspawn <arena>` sets where it appears. `/cq worldboss wand <arena>` gives the border stick: left-click blocks for corners, right-click to undo, sneak + right-click to show the border.
* It can never get past the border: it is pulled straight back to its spawn. Players must be inside to hurt it.
* It only attacks players, never breaks, burns or changes blocks (no explosions, no fire, no trampling, no snow trails), drops nothing and is never saved into the world. Creepers never explode, slimes never split, piglins and hoglins never turn into zombies.
* Rewards in `worldbosses.yml`: money and items for everyone who did at least 2% of its health, extra for the top 3, commands for the best player. The win is posted in chat and to Discord.
* It leaves after 5 minutes with nobody in the arena or after 30 minutes.
* `/cq worldboss list`, `arenas`, `next`, `spawn <boss> [arena]`, `stop [arena]`, `schedule on|off`. Players: `/quests worldboss`.

## Seasons

`/cq season <halloween|winter|spring|summer> on|off|auto`. Auto runs between the dates in `seasons` every year. A season brings two seasonal daily quests and its world boss, and is announced in chat when it starts and ends.

## Tutorial quest

"First Steps" starts right after the welcome quest: chop 4 logs, craft a crafting table and a pickaxe, mine 8 stone. It pays 5,000 money, a stone sword, food and torches as soon as it's done. Set `quests.tutorial-quest: ""` to turn it off.

## Invite a friend

New players type `/quests invitedby <name>` in their first 48 hours. They get 5,000 money and bread at once, and the friend gets 25,000 money and 2 diamonds when the new player finishes the tutorial. Players on the same connection don't count. `invites.milestones` runs commands at 3, 5 and 10 invites. `/quests invites` shows your count.

## Placeholders

`worldboss_next`, `worldboss_next_name`, `worldboss_alive`, `season` and `invites`.

## Test commands

`/cq test worldboss <boss>`, `worldbossnext`, `worldbossphase`, `worldbossstop`, `tutorial`, `season <id>`, `invite`.

## Tested

* Unit tests load all 24 bosses, check the weekly schedule, the arena border, season dates, and the tutorial and seasonal quests.
* On a real Paper 1.21.4 server the test player spawns every one of the 24 bosses. Paper latest and Folia latest start cleanly and switch a season on and off from the console.
