# CQuests 1.17.6 and CBosses 1.3.16: sizes, stone texture, softer hits, full falls

## Sizes
- Big bosses stand 3 to 4 blocks high and minis 1 to 2. Seven were outside that: the Abyssal Eye, the Broodmother, the Dusk Scorpion and Admiral Pinchworth grow to 3 blocks, the Listener, the Withered Tyrant and the Unmaker come down to 4.

## Texture where it fits
- 1.17.4 made every stone, moss and sculk skin flat. On big pieces that lost the look of rock and moss. The 229 big pieces have their texture again (Magmus, the Millstone Monk, the Gate Shade, the Moss Spirit, the moss creatures, the Listener). Small pieces stay flat, so there are no specks.

## Softer hits
- CBosses melee damage is about 30% lower on every tier: big 5 to 3.5, mythic 6 to 4, mini 3.5 to 2.5, chapter 4 to 3. Abilities scale with it. CQuests world bosses are 30% lower as well.
- A server that already has a bosses.yml keeps its own numbers. Change them with `/cbosses edit <boss> damage <value>`.

## Full falls
- 35 death animations tipped the boss half way and left it leaning in the air. They now go all the way down: the body hits the floor, bounces once and lies flat before it fades.

## Glitches
- The pumpkin faces (the Gourd King and the three pumpkin decorations) had 460 faces in the same plane as the head, which flickered. Each steps out of the plane.
- The Tide Tyrant's eye stalks stopped in the air above its head. They reach the head now.
