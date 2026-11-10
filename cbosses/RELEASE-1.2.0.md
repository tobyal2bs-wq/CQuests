# CBosses 1.2.0

The chapter 4 to 10 bosses and ten mini bosses are rebuilt from new reference pictures. Every model now
shows pixel texture, and every boss breathes, looks around and moves while it stands.

## Rebuilt bosses

- **Chapters 4 to 10**: the Gnome Brothers (a big and a little brother, each with its own idle), the Moss Spirit (staff and swaying grass), the Cyclops Ogre (moving jaw), Grubnose, the Orc Bruiser, Mudclub (with his club) and Ugor (heavy breathing). Each is 170 to 285 blocks.
- **Mini bosses**: Pack Goblin, Goblin King, Old Blindman (hood and beard), Garden Gnome, Ring Frog (puffing throat), Bog Orc, the Boo Twins (two ghosts that bob out of step), and an Angry Goose whose whole neck bends and weaves.
- **New minis**: Snapjaw (a swaying plant with a snapping jaw) replaces Sprout Sprite, the Mossling replaces Plump Pigeon, and the Cluck Rider replaces Fisher Duck.

## Texture and life

- Bodies use textured blocks (concrete powder, mud, granite, stripped logs, moss and more) in two or three tone patches, so nothing is a plain white or flat colour any more.
- New standing idle for two-legged bosses: breathing, weight shifting, the head looking around, arms drifting. Four-legged bosses sniff, wag and breathe.

## For ops

- `/cbosses chapter list` shows which boss guards each chapter.
- `/cbosses chapter set <chapter> <boss|default>` puts any boss on a chapter.
- `/cbosses chapter swap <a> <b>` swaps two chapters' bosses.
- Progress is stored by chapter number, so swapping or changing bosses never loses a player's progress.
- `plugins/CBosses/models/`: drop a model `.json` there (named by boss id) to replace that boss's look. It survives jar updates. A README in the folder explains it.

## Upgrading

Replace the jar and restart. Player data and chapter progress carry over unchanged.
