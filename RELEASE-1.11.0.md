# CQuests 1.11.0

Every world boss is now a real model built from blocks, with its own animations.

## Models

* **Built from blocks**: each boss is a jointed model of 40 to 140 display blocks (1876 in total), between 3 and 8 blocks tall. Heads, jaws, horns, armour plates, robes, tails, spider legs and slime insides are separate pieces with their own bones.
* **The real mob is still there**: it is invisible and carries the model, so its AI, pathfinding and hitbox work as before. The model turns with it and walks when it moves.
* **No more items on heads**: the halos from 1.10.1 are gone.
* **Cheap to run**: the model only updates every 3 ticks while a player is within 96 blocks, only for the pieces that moved, and the client smooths the motion in between.

## Animations

* **Three or more attacks each**: swipes, slams, sweeps, lunges, bites, charges, rears, pounces, leaps, spits, casts and more. Each ability plays its own animation, melee hits play one when a player is in reach, and a hit makes the boss flinch.
* **24 different entrances**: each boss arrives in its own way (rising from the ground, assembling piece by piece, dropping from the sky, lighting up, and so on). It cannot move or be hurt until it has finished.
* **24 different deaths**: each boss falls apart in its own way (collapsing, bursting, melting, freezing, crumbling, spinning away) before the fanfare.

## Settings

`world-bosses.models: true` in `config.yml` turns the models on or off for all bosses, and `model: none` on one boss in `worldbosses.yml` uses the plain mob for that boss.

## Self-test

`/cq worldboss selftest` now also checks that every model is drawn, plays every attack animation and every death. CI runs it on Paper 1.21.4, 26.2 and 26.3 and Folia 26.3.

## Upgrading

Replace the jar and restart. Delete `worldbosses.yml` to drop the old `halo:` lines (they are ignored either way).
