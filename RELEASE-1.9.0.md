# CQuests 1.9.0

Bigger chapter costs that read your own economy, co-op dailies, Pip as a boss fight helper, villagers that read the server's own recipes, daily money rolls and an elytra for finishing chapter 5. All player progress carries over.

## Upgrading from 1.8.x

1. Run `/cq backup`.
2. Replace the jar with `CQuests-1.9.0.jar` and restart. The five co-op quests are added to `quests.yml` (backup `quests.yml.before-1.9.0`). New config keys use their defaults until you add them.

## Chapter costs and your economy

* Chapter 2 costs 5M, then 10M, 20M, 35M, 50M, 75M, 100M, 150M and 250M for chapter 10 (`chapters.cost`).
* `economy.balance-placeholder` reads the balance from any PlaceholderAPI placeholder, for example `%vault_eco_balance%` or your own plugin's. Values like `$5,000,000.00`, `5.2M` and `12k` are understood.
* `economy.take-command` and `economy.give-command` run as the console with `<player>` and `<amount>`, for example `eco take <player> <amount>`. Leave them empty to use Vault.
* The "not enough money" message shows the player's balance with `<balance>`.

## Co-op dailies

Five daily quests need 2 to 4 players working within 16 blocks of each other at the same time: Barn Raising, Monster Sweep, Quarry, Great Wall and Feast. Progress only counts when enough friends do the same kind of task within 5 seconds, and an action bar hint says how many are missing. A co-op daily is only offered when friends are nearby. Set `together: 2` on any quest in `quests.yml` to make your own.

## Pip in boss fights

Pip can join 3 real boss fights per player (`adventures.pip-boss-help`), with a bow (hits from up to 24 blocks) or a sword (stays close and hits harder). Pick Pip in the boss menu. Pip can't be hurt and only the player sees Pip. Test fights don't use up Pip.

## Villagers know every item

Quest tips on how to craft, smelt, mine or place something are read from the running server's recipes and tags, so new items and blocks on newer Minecraft versions work without an update. `/cq test targets` checks every quest objective against the server and lists anything that can't be done. Tips can be turned off with `dialogue.how-to-tips`.

## Daily rewards

The daily's money rolls between 25% and 300% of its value (`daily.money-min-percent`, `daily.money-max-percent`), different for every player and day, with a message on a lucky or a quiet day.

## Chapter rewards

`chapters.rewards.<chapter>.items` and `.commands` are given when a player finishes that chapter. Chapter 5 gives an elytra; add your own command under `chapters.rewards.5.commands`.

## Other changes

* Farm wheat no longer counts for story quests, only for levels and early side quests.
* No chat message on join (`welcome.chat-message: true` brings it back).
* README no longer lists every version; see CHANGELOG.md.

## New test commands

`/cq test pip <bow|sword>`, `/cq test coop`, `/cq test daily`, `/cq test cost`, `/cq test targets` (works from the console).
