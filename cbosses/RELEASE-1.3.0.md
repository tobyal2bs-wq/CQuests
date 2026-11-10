# CBosses 1.3.0

The final polish: ten big bosses replaced with new ones, three minis grown into big bosses, 25 minis redrawn,
every model sized and centred properly, two-body bosses that really fight as two, evolving bosses, and op
commands to change any boss in game.

## New big bosses

These replace bosses that didn't work. They keep the same ids, so arenas, schedules and player data carry over.

- **The Lantern Angler** (was the Abyssal Eye): a deep sea anglerfish swimming through the air, glowing lure, snapping underbite.
- **The Antler King** (was the Hollow King): a gaunt king with a bone mask, huge antlers and a lantern of green fire.
- **Grimfang** (was Fenrir): a shaggy dire wolf with ice blue eyes and broken chains.
- **King Shellback** (was the Tide Tyrant): a giant crab with a coral crown and one huge crusher claw.
- **The Thunder Ram** (was the Storm Herald): a ram-headed giant with a thundercloud on its shoulders.
- **The Forge Mother** (was the Ember Queen): a smith giantess with a furnace in her belly and a forge hammer.
- **The Bone Collector** (was the Gravelord): a hunched ghoul with a sack of skulls and a soul lantern.
- **Old Tusker** (was Bloodtusk): a war boar with huge tusks, iron plates and a red banner.
- **The Stump Warden** (was Old Ironroot): a walking tree stump with glowing knot eyes and mushrooms on top.
- **The Gatekeeper** (chapter 2, was the Gate Shade): a hooded wraith with a giant key and a lantern.
- **The Frost Yeti, the Cinder Devil and Horngut** are now big bosses in the weekly rotation.

## Minis

Redrawn: Hay Golem, Snapjaw, Snik, Mister Pebbles, The Pink Burrower, Moss Imp, Mossling, Bark Ape, Old Hoodlum,
King Oldbeard, Farmer Grimbly, Gilded Mimic, Applecrab, Puffneck, Sir Mallard, Farmer Trotter, Jellyboo, Little Moo,
Mandrake, Old Shellby, Stumpy, and the two-body minis below. Every one has 150 to 300 textured blocks, a real face
and its own idle (ears twitch, hats flop, tails wag, tentacles ripple).

## Two-body bosses

Boo and Hoo (the Boo Twins), Toadstool and Puffball, and Bramble and Thimble (the Gnome Brothers) are now two
separate bosses. Each has its own health bar, they move differently and go after different players. When one
falls the other is enraged. Rewards are paid once both are down. Give any boss a partner with `partner:`.

## Sizes, centre and hitboxes

Big bosses stand about 3 to 3.5 blocks tall, mythic bosses 4 to 5, minis 1.5 to 2. Every model stands on the
ground with its weight over its centre, and its hitbox now covers most of its body.

## Evolving and mythic bosses

After a while in a fight a boss may evolve: it hits 25% harder, moves faster and heals a little, up to three
times (`evolve:` in config.yml). Mythic bosses always evolve and hit 25% harder (`mythic:` in config.yml).

## For ops

- `/cbosses edit <boss> [field value]` changes name, colour (`color #hex #hex`), title, health, damage, speed,
  armour, boss bar colour, theme, tier, evolve, partner or enabled, in game.
- `/cbosses enable|disable <boss>` turns a boss on or off.
- `/cbosses mythic [add|remove <boss>]` chooses which bosses are mythic.

## Data safety

bosses.yml, config.yml, arenas, minis, finale and chapter progress are written through a temporary file with a
`.bak` copy, so a crash or full disk mid-save never loses data. Redesigned bosses update their bosses.yml entry
and keep your rewards; the old file is kept as `bosses.yml.bak`. Players who leave are dropped from boss bars.

## Upgrading

Replace the jar and restart. Player data, chapter progress, arenas and rewards carry over.
