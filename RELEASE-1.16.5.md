# CQuests 1.16.5

Polish the existing vanilla block-display bosses without replacing the roster, designs, commands, abilities or rewards.

- Remove permanent aura circles and shared entrance rune circles; replace the common dirt eruption with theme effects.
- Give every model its own idle/walk timing and entrance performance; keep jaw, limb and held-item animation.
- Cut plates at elbow/knee hinges. Correct knee bend geometry, unreachable foot targets and all attached descendants.
- Keep passenger rotation at zero; face the direction of travel and turn across the shortest angle.
- Switch facial visibility immediately, avoiding interpolation through zero-sized expressions.
- Correct visibility checks for pieces drawn below or outside the carrier's passenger box; keep normal frustum culling for parts that fit.
- Minis have 2,000 HP; big, mythic and chapter bosses have 5,000 HP. Existing files get a one-time health-only migration with backup; rewards and other settings remain.
- Regression tests sample all models throughout idle, walk, attacks and openings, checking joint attachment and client display matrices.

The separately commanded friendly Mossback is provided by CBosses. Quest commands, dialogue, progression, economy and NPCs are unchanged.
