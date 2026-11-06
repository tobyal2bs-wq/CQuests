# CQuests 1.15.0

Goes with CBosses 1.2.0.

## Changes

- World boss models are textured: every flat concrete block is now its speckled concrete powder twin, so boss skin and cloth show pixel grain in game.
- Boss models can be changed without touching the jar. Put `.json` model files in `plugins/CQuests/models/` (same format as `worldboss-models.json` in the jar). A model there replaces the built-in one with the same id. Updates never touch that folder.
- Player progress is not stored with the models, so changing, adding or swapping bosses never loses quests, chapters or rewards.

## Chapter bosses

Chapter bosses come from CBosses 1.2.0, which rebuilds chapters 4 to 10 (the Gnome Brothers, the Moss Spirit, Gulp the Cyclops, Grubnose the Troll, Borka the Bruiser, Mudclub and Ugor). Ops can move them around with `/cbosses chapter swap <a> <b>` or `/cbosses chapter set <chapter> <boss>`; who has beaten which chapter is kept by chapter number.

## Upgrading

Replace the jar and restart.
