# CBosses 1.0.0

The first release of CBosses: 52 animated block-model bosses for Paper and Folia, with weekly, seasonal,
chapter and finale fights, a settings screen and full WorldGuard support.

## The bosses

| Group | Count | Bosses |
| --- | --- | --- |
| World bosses | 25 | Slagheart, Warlord Gruk, the Grand Augur, the Crimson Oni, Thunderback, Gorehorn, the Abyssal Eye, Overgrowth, the Prism Sentinel, the Tiki Warden, the Hollow King, the Broodmother, the Ironhide Behemoth, Fenrir, the Tide Tyrant, the Void Walker, the Storm Herald, the Pharaoh, the Executioner, the Ember Queen, the Gravelord, Captain Brine, the Keywarden, Bloodtusk, King Gloop |
| Legends | 4 | The Listener Below (Warden), the Withered Tyrant (Wither), Vorthax the Ender Wyrm (a flying Ender Dragon), the Gale Sovereign (Breeze) |
| Finale | 1 | The Unmaker, who wakes once all four legends have fallen |
| Winter | 3 | Killer Claus, Frostbottom, Old Man Winter |
| Summer | 3 | Sunscorch, Admiral Pinchworth, Brain Freeze |
| Spring (Easter) | 3 | Clucksworth, the Killer Bunny, the Cocoa Colossus |
| Halloween | 3 | The Great Gourd, the Headless Horseman, the Hexmother |
| Chapter bosses | 10 | Brakka, the Gate Shade, Sir Oakheart, the Vault Mimic, the Crypt Knight, Iron Tusk, the Reef Hulk, the Ember Knight, the Choirmaster, the Sculk Herald |

- **Hand-built models.** Every big boss is 150 blocks or more and every block is there for a reason: faces painted
  pixel by pixel, armour with rims and rivets, torn hems, fur, glowing cracks that follow the plates, and props
  that tell you who the boss is. Chapter bosses are smaller and simpler on purpose, one after each CQuests chapter.
- **Its own entrance.** The Grand Augur's crown floats down onto his head last, Killer Claus climbs out of his
  sack, the Vault Mimic is just a chest until it stands up, Clucksworth hatches out of a painted Easter egg.
- **Its own death.** The Horseman's pumpkin is thrown, the Pharaoh pours away as sand, Fenrir freezes and
  shatters, the Void Walker is sucked into a point and bursts, the Unmaker shatters from the heart outward.
- **Its own attacks.** Every ability plays the boss's own move, with a wind-up you can read and dodge.
- See every boss turning, attacking and dying in the 3D viewer: https://claude.ai/artifact/NbYXjJCKyRwZ2oTmETby7k

## Settings screen

- `/cbosses settings` shows every option of `config.yml` on five pages: effects and lag, the weekly boss, fights,
  chapter bosses, and seasons, finale and WorldGuard.
- On 1.21.6 and newer it is the game's own settings screen: buttons that cycle through choices, sliders for
  numbers, text boxes, a Save button and live boss statistics at the top. Older servers get a chest menu where a
  click changes a value.
- `/cbosses settings set <path> <value>` changes one option from chat or the console. Every change is saved and
  applied at once.

## Permissions

- Controlling bosses (spawn, stop, test, arenas, schedule, settings) is for operators and anyone with
  **`bosses.use`**. `cbosses.admin` includes it. CQuests uses the same permission.
- Everyone can see when the next boss wakes with `/cbosses next`.

## Fights

- Weekly schedule at your arena, seasonal bosses while their season is on, private chapter bosses after each
  CQuests chapter, and the finale.
- No boss ever breaks, burns or places a block.
- Shockwaves, meteors, spikes, sonic booms, minion waves and more, themed per boss (25 themes, including the new
  wind theme for the Gale Sovereign).

## Light on servers and clients

- Models only update near players and the client smooths the motion; particles and flying blocks have hard caps.
- `effects.model-detail` drops the finest pieces on busy servers.
- Folia-safe. Tested on Paper 1.21.4, Paper 26.2, Paper latest and Folia latest: every boss appears, runs every
  attack and plays its death.

## Install

1. Put `CBosses-1.0.0.jar` in `plugins/` (Paper or Folia 1.21.4 and newer, Java 21).
2. Optional: WorldGuard, PlaceholderAPI, CQuests.
3. `/cbosses arena setspawn main`, then `/cbosses test the_listener` or `/cbosses` for the boss menu.
