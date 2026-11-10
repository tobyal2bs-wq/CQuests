# CBosses studio redesign

CBosses now lives in this repository under `cbosses/`. The `CBosses` workflow builds it, runs its tests and boots
Paper 1.21.4, Paper latest and Folia latest with every boss.

## Rebuilt by hand
Grubnose the Troll, Mudclub, King Oldbeard, Hay Golem, The Bone Collector (gravelord), The Forge Mother
(ember_queen), Old Tusker (bloodtusk), The Clockwork Colossus, Mayor Grumble, Sunscorch, the Gourd King, the three
decor pumpkins and the Hollow Mage. Each one has its own idle, walk and attacks with a wind-up, the weight going
through the hips and legs, and a follow-through. The pumpkins have carved faces (idle, happy, surprised, angry,
sleepy, wink) and the Gourd King's face changes with the fight (idle, angry, hurt, rage, dead).

These models are in `tools/models/v14_studio.py` (helpers in `v14_kit.py`) and skip the old automatic polish and
refine passes, which were what detached King Oldbeard's crown and Grubnose's nose. Every older biped boss now uses
the same new attack set.

## New bosses
- Big: Rootmaw (the mandrake), Brewgut (the tavern orc), and three Hollow Mage variants: The Cinder Hollow, The Rime
  Hollow and The Bramble Hollow.
- Mini: Peeper (the red googly-eyed critter), Bogwart (frog-man), Old Pip (gnome elder) and Sproutbeak.

There are now 94 bosses: 41 weekly, 3 mythic, 12 seasonal, 8 chapter and 30 minis.

## Commands a boss runs
In `bosses.yml`, per boss:
```yaml
  my_boss:
    spawn-commands: ["broadcast %bossname% woke up at %x% %z%"]
    defeat-commands: ["broadcast %bossname% fell to %player%"]
    group-commands: true        # false skips the group lists from config.yml for this boss
```
In `config.yml`, for every boss of a kind (`bosses`, `seasonal`, `minis`, `chapter`):
```yaml
rewards:
  commands:
    minis:
      every-player: ["give %player% emerald 2"]
      top-player: []
      on-spawn: []
      on-defeat: []
```
Group commands run first, then the boss's own. Placeholders: `%player%`, `%place%`, `%boss%`, `%bossname%`,
`%world%`, `%x%`, `%y%`, `%z%`.

## Viewer
`docs/boss-viewer.html` shows every model with its real block textures, attacks, entrance and death.

## Rebuilding the models
`tools/models/gen_models.py` needs the vanilla entity textures in `tools/models/tex/` (not in git). Download them
from a Minecraft 1.21 assets copy, then run `python3 gen_models.py`, `python3 ../gen_bosses_yml.py` and
`python3 ../viewer/build_viewer.py`. CQuests world bosses pick up the new looks with
`python3 tools/worldboss/sync_visuals.py cbosses` from the CQuests root.
