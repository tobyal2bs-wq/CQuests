# CQuests 1.12.0

World boss models get elbows, proper grips, hit zones and more detail, and cost less to run.

## Held weapons

* **Gripped in the fist**: every boss with a weapon holds it by the handle with fingers wrapped round it, blade up and forward, the way a player holds a sword. Staffs stay upright.
* **Elbows**: every arm is split at the elbow and bends, at rest and in every attack. Empty hands have fingers and a thumb.

## Hit zones

Where you hit a boss now matters. Each boss has invisible hit boxes on its head, its weak spot (the glowing piece on its body), its body, arms, tail and weapon. They follow the model as it moves and attacks.

| Zone | Damage |
| --- | --- |
| Weak spot | x2.5 |
| Head | x1.5 (x1.2 with a metal helmet) |
| Body, legs | x1 |
| Arms, tail | x0.8 |
| Armoured body | x0.6 |
| Weapon | x0.3 |

A hit on a zone is a normal attack with your weapon, so enchantments, crits, sweeps and the cooldown all count, and the action bar tells you what you hit. The real mob underneath is now only as tall as the legs and lower body, and its melee swing still lands at the end of the model's arm. The name tag is gone from bosses with a model; the boss bar shows the name.

## Animations

The attack animations were rebuilt around the elbows: wind-up, weight shift onto the front foot, a follow-through after the hit, and the forearm snapping straight on the strike.

## More detail

King Gloop and Sunscorch were rebuilt, and the Killer Bunny, Volatile Colossus, Ruinmaw, Executioner, Old Man Winter and Fenrir got a detail pass (claws, toes, collars, chains, runes, embroidery, scars, belts). Every boss is now between 76 and 133 blocks.

## Less lag

* Bosses update half as often when no player is within 28 blocks; the client blends the longer gap so it still looks smooth.
* Model blocks are drawn to about 50 to 90 blocks away instead of up to 190.
* Hit boxes only move when their part moved.

## Upgrading

Replace the jar and restart. Nothing to change in your configs.
