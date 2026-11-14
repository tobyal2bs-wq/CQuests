# CBosses 1.3.5

## Fixed

- Bosses no longer break apart into loose, tilted blocks in game. Every block that was longer in one direction (arms, legs, plates, horns) was drawn at the wrong angle as soon as it turned, because its rotation was worked out wrongly. In-game bosses now match the preview. A new test checks every boss, standing and walking.
