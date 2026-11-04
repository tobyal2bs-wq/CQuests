# CQuests 1.13.0

Every seasonal world boss is rebuilt to be funny, four new seasonal bosses join them, and operators get a world boss control panel.

## Seasonal bosses

Two bosses per season, each with a joke in its design, its own entrance and its own death.

| Season | Boss | What it is | Arrives | Dies |
| --- | --- | --- | --- | --- |
| Halloween | The Headless Horseman | A skeleton-horse rider with a scythe, green ghost fire for a neck and his pumpkin head under one arm | The head bounces in first, then the body rides out of the flames to catch it | Burns from the hooves up; the pumpkin flies up and bursts into fireworks |
| Halloween | **The Great Gourd** (new) | A walking pumpkin with a carved grin, a hinged lid with a tiny witch hat, a giant lollipop and a treat bucket | A seed sprouts and swells in three gulps, then pops its lid | The lid blows off, candy fountains out, the pumpkin caves in |
| Winter | Old Man Winter | Ugly Christmas sweater, slippers, a huge beard and a candy-cane staff | Floats down out of the sky, grumbling | Sneezes his head off and melts into a puddle |
| Winter | **Frostbottom** (new) | An angry snowman with a top hat, a long carrot nose, twig arms and an ice-ball club | Three snowballs roll in and stack up, the hat flops on last | The head pops off and rolls away, the rest melts |
| Spring | The Killer Bunny | A chubby white rabbit in a red headband and eyepatch, with a carrot bandolier, a carrot "cigar", one bitten ear and bloody claws | A tiny harmless rabbit that keeps growing | Puffs up and pops into fluff |
| Spring | **Clucksworth** (new) | A giant furious chicken wearing half an eggshell as a helmet, with flowers in its feathers | A giant egg wobbles, cracks, and it bursts out | Explodes into feathers; only the eggshell falls |
| Summer | Sunscorch | A melting little sun on holiday: sunglasses, sunscreen on its nose, tongue out, a rubber-duck float ring and a cocktail umbrella | Cannonballs out of the sky onto its float | Gets a puncture, zooms round blowing out air, pops into a tiny sunset |
| Summer | **Admiral Pinchworth** (new) | A crab with googly eye stalks, a moustache, an admiral's hat, one huge claw and a sandcastle on its back | Digs up out of the sand sideways, snapping to a drumroll | Flips onto its back, legs kicking, the sandcastle collapses on it |

All of them walk, attack and take hit-zone damage like the other bosses (weak spot, head, body, arms). 28 bosses in total, all vanilla blocks.

## Boss control panel (operators)

`/quests` now shows a **World boss controls** button for anyone with `cquests.admin`, or open it with `/cq worldboss menu`.

* **Left-click** a boss: it spawns at your main arena (a glowing egg means it is alive).
* **Right-click**: a test spawn next to you.
* **Shift-click**: stop that boss.
* Bottom row: weekly schedule on/off, set the main arena where you stand, stop all, self-test, back.

## Announcements

* A spawn sends a framed announcement to everyone with the boss name, title and where it is.
* The kill message names who landed the killing blow and the top 3 by damage, with their damage and share, in gold, silver and bronze.

## Upgrading

Replace the jar and restart. The four new bosses are added to your existing `worldbosses.yml` automatically; bosses you already have are left as they are.
