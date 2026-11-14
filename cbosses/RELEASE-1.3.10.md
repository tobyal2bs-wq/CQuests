# CBosses 1.3.10

The three approved creatures now ship as regular 5,000 HP world bosses: Millstone Monk, Moonwake Manta and Thorncoil Basilisk. No chapter or seasonal assignment was added.

- Manta: feeding curl, moonwake surge and lunar updraft; slow articulated wing beats, luminous back weak spot, glow/rod arrival and departure.
- Basilisk: thorncoil lunge, leaf hood warning and rootcoil slam; attached jaw and fangs, exposed jaw weak spot, falling leaves and moss breakup.
- Every boss uses time-based walk blending, eased attack/hit weights and smooth shortest-arc turning. Distant idle models correctly skip alternate pose updates while new attacks/hits remain responsive.
- CQuests enables the existing fly animation layer on flying carriers.
- Low detail removes optional trim while keeping eyes, limbs, jaws and joints.

Validation: complete animation/display reconstruction and face exclusivity tests run for every shipped model. All 88 CBosses models were rendered in idle/walk/attack for visual review; CQuests has its separate full-rig checks. Existing model geometry, rewards, commands, chapter IDs and settings are preserved.

Install: stop the server, back up both old JARs and data folders, replace only the JARs, then start. Keep all plugin data and configuration. Missing boss defaults are merged by the existing upgrade path. No resource pack.

Commands remain `/cbosses spawn <id> here`, `/cq worldboss spawn <id> <arena>` and `/cq test worldboss <id>`. IDs: `millstone_monk`, `moonwake_manta`, `thorncoil_basilisk`.

Rollback: stop and restore the old JARs and data folders together.

Automated server checks do not prove production-client appearance or player-load performance. No claim of universal Minecraft/fork compatibility is made.
