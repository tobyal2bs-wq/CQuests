# CQuests 1.14.0

## World bosses look and move far better
- Every world boss model now has at least 120 blocks. A finishing pass adds layered shoulder plates, knee guards,
  chest badges, spines on beasts, torn hems, rivets on metal, light and dark shading patches and glowing veins in
  the boss's own colour.
- Entrances end with the armour plates springing out and clicking into place from the feet up, then the veins light.
- Deaths start with the veins going dark and the armour plates thrown off before the boss's own death plays out.
- New settings under `world-bosses:` in `config.yml`: `model-detail` (high, medium, low), `model-update-ticks`,
  `model-view-distance`, `max-shards-per-death` and `particle-multiplier`.

## Every text can be changed
- Every chat line, title, action bar, menu line and command reply that used to be written into the code is now in
  `messages.yml` under `text:`, grouped by feature. Words in angle brackets like `<player>` are filled in.
- Lines added by an update are written into your own `messages.yml` by themselves, so you can find them.

## Works with CBosses
- With the CBosses plugin installed, CQuests leaves the world bosses to it (`world-bosses.defer-to-cbosses: true`),
  so there are never two bosses at once. CBosses adds chapter bosses after every chapter and the finale.
