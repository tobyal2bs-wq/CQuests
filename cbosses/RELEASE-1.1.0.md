# CBosses 1.1.0

93 bosses, hourly mini bosses with op spawn spots, a spawn-here menu, faces that change mid-fight, and legs
that bend at the knee with feet that stay flat on the ground.

## New bosses

- **30 mini bosses** (3000 health) that wake on their own timer, every hour by default: Bark Ape, Old Blindman, Bog Orc, King Oldbeard, Frost Yeti, Farmer Grimbly, Gilded Mimic, Plump Pigeon, Cinder Imp, Apple Crab, Pink Burrower, Moss Imp, Garden Gnome, Angry Goose, Pack Goblin, Goblin King, Sprout Sprite, the Cap Brothers, Puffneck, Mallard, Piggy Farmer, Ring Frog, Ghost Jelly, Hay Golem, Fisher Duck, Little Moo, the Boo Twins, Mandrake, Mossy Turtle and Stumpy.
- **New big bosses** (5000 health) in the weekly rotation: Archmage Bramblebeard, the Hollow Mage, Gorrak, the Rotting Giant, the Dusk Scorpion, Clockwork Colossus, Mossback, Grave Marshal, Mayor Grumble, the Shulker Matriarch and Old Ironroot.
- **The Gourd King** replaces the Great Gourd at Halloween. His pumpkin face changes as he fights: calm, angry when he attacks, hurt when hit, lit up with rage below half health, and dead.
- Redone: Grand Augur (tall gold crown, gold cuffs, glowing crystal staff), Old Ironroot (a pale mossy golem with vines and dandelions), Mayor Grumble (now a person with a coat, sash, chain of office, top hat and gavel), the Shulker Matriarch (a painted shell, a face and four little shulkers).
- Mythic bosses have 8000 health.

## For ops

- `/cbosses menu`: left-click any boss to spawn it where you stand. It only attacks players and never breaks blocks.
- `/cbosses minis`: a menu for mini boss spots. Add a spot where you stand, show the spots as barrier markers, pick fixed, random or mixed spawning, set how often minis wake, how many at once and which bosses each spot uses, or wake one now.
- `/cbosses decor place <pumpkin>`: three pumpkins that sit and pull faces (happy, surprised, angry, sleepy, wink). They only exist while a player is near.

## Under the hood

- Legs have knees, and feet stay flat on slopes and steps.
- Decor and mini bosses are cleaned up on shutdown and reload; nothing is left in the world.

## Upgrading

Replace the jar and restart. New keys (`minis`, `arenas.here-radius`) are added to your config. Boss health uses the new tiers unless you set it yourself in `bosses.yml`.
