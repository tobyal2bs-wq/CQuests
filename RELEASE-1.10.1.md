# CQuests 1.10.1

World bosses get animations and are checked on every server version.

## Animations

* **Spawn ritual**: two seconds before a boss appears, a rune circle closes in on the spawn, light rises and the ground rumbles, then lightning and a burst.
* **Attacks you can see coming**: the boss swings and a red ring (or a marker under your feet for lightning) shows where the attack will land a moment later, so you can dodge it. Leaps mark the landing spot and hit on landing.
* **Hits**: a heavy sweep and crit effect when the boss hits a player.
* **Death**: its colour spirals up out of the body, small blasts go off, then a big burst, a beam of light and fanfare.
* **Halo**: an item floats and spins above each boss (`halo:` in `worldbosses.yml`), drawn with a display entity that costs almost nothing.

## Lighter fight loop

One nearby-player check per half second instead of three, the boss bar text is only rebuilt when the health number changes, particles are only drawn when a player is close, and particle settings are worked out once per fight.

## Self-test

`/cq worldboss selftest` (works from the console) spawns every boss near the world spawn, runs every attack, plays the death animation and removes them, then reports. CI runs it on Paper 1.21.4, 26.2 and 26.3 and Folia 26.3: 24 of 24 bosses appeared and 384 attacks ran on each.

## Upgrading

Replace the jar and restart. Delete `worldbosses.yml` (or copy the `halo:` lines from the bundled one) to get the halos.
