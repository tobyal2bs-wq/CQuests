# CQuests 1.14.0

Every world boss is redesigned, any arena can become a boss spot on its own timer, and world bosses get real
falling meteors and ground shockwaves.

## New world bosses

41 world bosses, every one a hand-built block model with its own entrance, attacks and death. The models are
shared with the CBosses plugin, so both plugins show the same bosses.

| Group | Bosses |
| --- | --- |
| 25 general bosses | Slagheart, Warlord Gruk, the Grand Augur, the Crimson Oni, Thunderback, Gorehorn, the Abyssal Eye, Overgrowth, the Prism Sentinel, the Tiki Warden, the Hollow King, the Broodmother, the Ironhide Behemoth, Fenrir, the Tide Tyrant, the Void Walker, the Storm Herald, the Pharaoh, the Executioner, the Ember Queen, the Gravelord, Captain Brine, the Keywarden, Bloodtusk and King Gloop |
| 4 legends | The Listener Below (Warden), the Withered Tyrant (Wither), Vorthax the Ender Wyrm (Ender Dragon) and the Gale Sovereign (Breeze) |
| Winter | Killer Claus, Frostbottom, Old Man Winter |
| Summer | Sunscorch, Admiral Pinchworth, Brain Freeze |
| Spring (Easter) | Clucksworth, the Killer Bunny, the Cocoa Colossus |
| Halloween | The Great Gourd, the Headless Horseman, the Hexmother |

- **150 blocks or more** each (the Grand Augur is built small and chunky on purpose), with faces painted
  pixel by pixel, armour with rims and rivets and props that tell you who the boss is.
- **No two entrances or deaths alike.** Killer Claus climbs out of his own sack, Frostbottom stacks himself one
  snowball at a time, Clucksworth hatches from a painted Easter egg; the Pharaoh pours away as sand, Fenrir
  freezes and shatters, the Horseman's pumpkin is thrown.
- Each ability plays the boss's own move.
- Seven old bosses were replaced (Molten Colossus, Frost Jarl, Cinder Sovereign, Volatile Colossus, Ruinmaw,
  Tempest, Pale Watcher). They are removed from your `worldbosses.yml` on the first start; the new ones are added.

## Boss spots

Any arena can wake bosses on its own timer, apart from the weekly boss.

- `/cq worldboss interval <arena> 2h` (or `400h`, `90m`, `1d12h`, `off`) makes it a spot.
- A different boss wakes every time, and each fight picks a new patrol pattern (orbit, figure eight, zigzag,
  wander or star), turning direction, size and speed. While fighting, it closes in its own way too.
- Spot bosses attack any player and still never break, burn or change a block.
- `/cq worldboss spots` lists every spot and when its next boss wakes. A warning goes out 5 minutes before.
- Spots run even when CBosses has taken over the weekly boss.
- Settings: `world-bosses.spots` (`warn-minutes`, `seasonal`, `bosses`).

## No-pass areas

- `/cq worldboss nopass <arena> here [radius]` adds a circle the boss can never enter.
- `/cq worldboss nopass <arena> corner`, run at two opposite corners, adds a box.
- `list`, `remove <n>`, `clear` and `show` manage them. A boss or minion that ends up inside is put straight back.

## Shockwaves and meteors

- Shockwaves and quakes throw a ring of the ground's own blocks that rolls outward and sinks away.
- The new **meteor** ability drops real falling rocks: marked on the ground, they crash a second later and leave
  glowing broken pieces for a few seconds.
- These are block displays, never real blocks. `world-bosses.max-block-effects` (48) caps how many are alive at
  once on the whole server; past it the effect falls back to particles.

## Permissions

- Controlling bosses (`/cq worldboss`, `/cq test worldboss`, the boss panel and the border stick) is for operators
  and anyone with **`bosses.use`**, the same permission as CBosses. `cquests.admin` includes it.

## Quest bosses

- A quest boss only attacks the player doing the quest, and only that player can hurt it. Pets, friends and their
  arrows never could; now splash and lingering potions from anyone else don't touch it either.

## Also in this version

- Every chat line, title, action bar, menu line and command reply is in `messages.yml` under `text:`.
- New `world-bosses:` settings: `model-detail`, `model-update-ticks`, `model-view-distance`, `max-shards-per-death`
  and `particle-multiplier`.
- With CBosses installed, CQuests leaves the weekly boss to it (`world-bosses.defer-to-cbosses: true`).

## Upgrading

Replace the jar and restart. New bosses are added to your `worldbosses.yml` and the replaced ones removed; bosses
you changed yourself keep your changes.
