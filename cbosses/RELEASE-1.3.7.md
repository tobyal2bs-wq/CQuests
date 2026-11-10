# CBosses 1.3.7

Polish the existing vanilla block-display bosses without replacing the roster, designs, commands, abilities or rewards.

- Remove permanent aura circles and shared entrance rune circles; replace the common dirt eruption with theme effects.
- Give every model its own idle/walk timing and entrance performance; keep jaw, limb and held-item animation.
- Cut plates at elbow/knee hinges. Correct knee bend geometry, unreachable foot targets and all attached descendants.
- Keep passenger rotation at zero; face the direction of travel and turn across the shortest angle.
- Switch facial visibility immediately, avoiding interpolation through zero-sized expressions.
- Correct visibility checks for pieces drawn below or outside the carrier's passenger box; keep normal frustum culling for parts that fit.
- Minis have 2,000 HP; big, mythic and chapter bosses have 5,000 HP. Existing files get a one-time health-only migration with backup; rewards and other settings remain.
- Regression tests sample all models throughout idle, walk, attacks and openings, checking joint attachment and client display matrices.

Friendly Mossback:

- `/mossback spawn` places one at your feet; `/mossback spawn x y z world` also works from the console.
- `/mossback list` counts saved friendly Mossbacks; `/mossback remove` removes the nearest within 12 blocks.
- Spawning/removing uses the existing `bosses.use` permission. Anyone may right-click to ride; sneak to dismount. One rider per Mossback.
- Wanders slowly on flat **DIRT** only. Grass blocks, paths, coarse dirt, stone, steps and holes stop it. No climbing or hostile AI.
- Spawn any number independently of arenas and timers. Locations persist in `friendly-mossbacks.yml`; unloaded chunks release the live model and restore it when loaded.
