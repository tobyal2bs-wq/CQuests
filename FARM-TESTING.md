# Test the farm on a small plot

For the click-to-upgrade anvil and its current/next hoe screen, see [WORKSHOP-1.3.4.md](WORKSHOP-1.3.4.md). Players only right-click the registered anvil; the commands below are one-time administrator setup.

Use WorldEdit and WorldGuard. Pick a small test plot away from other players' builds, fill it with farmland/water and mature wheat, and use Survival mode (Creative harvesting is intentionally disabled).

1. Select opposite plot corners with the WorldEdit axe (`//wand`), then `//expand vert` so the region includes the crop height. Define a new region: `/rg define cquests_farmtest`. Optionally `/rg flag cquests_farmtest build deny` verifies protected-field harvesting.
2. As an admin run `/cq farm wand wheat_test`. With this stick, left-click the perimeter corners in order (at least three; four for a rectangle). Right-click undoes a corner. The polygon may follow a curved or irregular perimeter.
3. Save it: `/cq farm save wheat_test cquests_farmtest`.
4. Leave the region and re-enter in Survival with a free hotbar slot. The free first-tier personal hoe equips automatically. Left-click one mature wheat crop. Only that crop is harvested, green particles appear, and it regrows after about one second. The default first-tier reward is 10 custom skill XP; vanilla XP stays unchanged.
5. Leave the farm: the personal hoe is removed and its unlocked tier stays in your private locker. Re-enter to equip it again. Normal commands and containers are blocked inside the field for ordinary players; administrators bypass command restrictions.

For the upgrade GUI, place an anvil outside the crop plot, look at it and use `/cq farm anvil`, then right-click it. `/cq farm menu` also opens the workshop for an admin. Upgrades require the listed skill level and money from the registered Vault economy. Test with an ordinary Survival player too: OP/WorldGuard bypass permissions can mask region-protection mistakes.

These are real farm setup commands, not a temporary sandbox: keep the plot small and back up your configuration before changing an existing farm. Farm outlines are saved in `farming.yml`; `/cq merchant test` does not create a farm.
