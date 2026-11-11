# CQuests 1.17.0 and CBosses: loot crates, Chest Tokens, seasonal decorations

## Loot crates (CQuests)
- `/cq crate place` puts a wooden crate spot where you stand; placed in the air, it falls to the ground. Region protection does not block it or its opening.
- Using a crate (right or left click) breaks it open and drops one pick from `crates.loot` in config.yml (5 diamonds, 1 netherite ingot, ...). A placed spot comes back after `crates.respawn-minutes`.
- `crates.wild.count` crates also hide on the surface around the main world's spawn and move somewhere else after a while.
- Very rarely a crate also drops a **Chest Token**: a glowing sunflower that sparkles on the ground. The odds are rolled fresh every day between 1 in 10,000 and 1 in 200,000 (`crates.token`). `/cq crate` shows today's odds.
- The token cannot be placed, crafted or composted, and only real tokens count in trades: a renamed sunflower never matches.
- `/cq crate token [player] [amount]` gives tokens, for example to set up trades in the merchant editor.
- New merchant **Tobin the Token Keeper** (`tokenkeeper` in merchants.yml) trades tokens for rewards. Set his spot like any merchant and change his offers in the editor.
- New quest objective `FIND ANY <amount>` counts opened crates. Daily quests `crate_hunt` (find 2) and `crate_hunt_far` (find 4) come from Marigold. When you take one, she tells you roughly where the two nearest crates are (`/cq crate hint` repeats it for ops).

## Seasonal decorations (CBosses)
- `decor_gingerbread`, `decor_gingerbread_girl` (Christmas) and `decor_egg_pink`, `decor_egg_blue`, `decor_egg_mint` (Easter), next to the pumpkins.
- Mostly happy faces, sometimes sad, and now and then a little hop in place.
- `/cbosses decor place <model>` puts one on top of the block you look at, or on top of the decoration already there, so they stack. Removing one brings the ones above it down.

## Bosses (CBosses)
- Back to the original stacked-slice look.
- New opening: walkers form high above their spot, drop, land with a squash and a puff of dust, then roar. Flyers swirl in.
- Attacks lean back into the wind-up and drive into the hit. About 30% less damage.
- The model no longer flips round when a boss is shoved or backs off.
- No dust rings or ground waves (`effects.ground-waves`, off by default).
