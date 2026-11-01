# CQuests 1.2.0 validation — 2026-11-01

Continued from the existing Claude branch, after 1.1.0 commit `9e289492bc3e750deeb278ecd2f3b727c34cfdc6`. The original Claude base remains `4a1ca9404bbf21c17c2adb8326e7dd56eb500216`.

## Final artifact

- JAR SHA256: `38236ea094448d232679339be2ce83b786b9aab9dc9a9148ea3e44b6bbc64671`.
- Gradle 8.14.3 / Temurin Java 21: **32 tests, zero failures or errors**. Every plugin class is Java 21 bytecode (major 65); plugin metadata is 1.2.0.
- Original 101 NPC definitions remain structurally unchanged; eight additional residents make 109 total. Original quests and generator content remain identical apart from checkout newline normalization. Regenerating the story retains equivalent NPC/quest data.
- New tests cover concave/reversed/inverse polygons, invalid outlines, bounded selections, every level boundary, low-XP curves, combined level/task gates, custom skill/tool persistence and cave rejection. Existing story, visibility, terrain, directions, pagination and recovery tests still pass.

## Real server matrix

The **same final JAR hash above** was installed in each isolated test server. Servers bound to localhost; no hosted player data or economy was used.

| Server | Runtime | Result |
|---|---|---|
| Paper 1.21.4 build 232 | Java 21 | Two boots; story/client regression and persistence passed |
| Folia 1.21.4 build 6, two region tick threads | Java 21 | Two boots; story/client regression and persistence passed |
| Paper 26.2 build 135 | Java 25 | Native dialogue, speech, farm and integration checks passed; clean shutdown |
| Folia 26.2 build 7, two region tick threads | Java 25 | Native dialogue, speech, farm and integration checks passed; clean shutdown |

The older-server client suite explicitly disables animated speech and custom-level gates in its fixture to exercise the compatible book/menu path and original story sequence. It checks default-off boss bars, journal opening, single-use rewards, explicit acceptance, future-chapter hiding, tracking/directions toggles, menu item locking, repeated 10k world scattering, preserved active quests and preferences after a full restart. Paper also exercises real End void rejection at radius 10 and Nether lava/roof rejection. Console reload, backup and old saved-player preservation checks passed on both older engines.

The 26.2 servers used WorldGuard `7.0.20-SNAPSHOT+2403-4181ebf`, WorldEdit `7.4.6-SNAPSHOT+7634-f4bf495` and PlaceholderAPI 2.12.3. Paper used Vault 1.7.3; Folia used VaultUnlocked 2.20.1. A **validation-only economy provider** registered with Vault supplied exact balances and withdrawals. This verifies CQuests' integration, not the user's custom economy implementation.

Two Mineflayer 4.39 clients connected through ViaVersion/ViaBackwards 5.12.2 using the supported 26.1 client protocol. Thus these are server/protocol tests, not a visual test in a graphical 26.2 client.

Each modern server passed 26 farm/progression assertions, plus native dialogue and two-client observations:

- Exact named WorldGuard region lookup and fail-closed missing-region handling.
- Free tool acquisition, level restriction, exact 5,000 withdrawal, tier ordering and rejected replay without another charge.
- Duplicate bound tools collapse to one personal tool; commands are denied in the farm.
- One mature wheat becomes air immediately; adjacent wheat is untouched. Duplicate hits award XP once. Outside crops and carrots remain unchanged and give no XP.
- Fully grown wheat returns after 20 region ticks. A real client block-dig packet harvests successfully through a WorldGuard region with `build: deny`.
- Base XP/multiplier rounding, wheat counter and custom level crossing behave as expected. Both XP gain and level-up leave vanilla XP untouched.
- Leaving strips the carried hoe while retaining its purchased tier; returning restores one tool. Actual PlaceholderAPI resolves the player's level and tool tier.
- Actual `minecraft:multi_action` packets contain the native choices. The server-generated response token successfully claims the welcome reward once through the farm's command restriction.
- Letter-by-letter private text-display updates and click sounds reach the talking player. A nearby second client receives none of the private speech. Buffered player chat arrives after the speech completes.
- Each client run recorded two native dialogs, 12 measured updates containing the first sentence's prefix, one successful welcome claim and one custom level-up. Click sound packet counts vary with sentence skipping.

On final Paper 26.2, `/cq camp` placed exactly six NPCs — five camp residents and the daily villager — with zero skipped searches. All server processes shut down cleanly. No CQuests stack traces or Folia ownership/thread violations were found in the final runs. The host initially ran out of native memory when builds overlapped servers; final checks ran sequentially with bounded JVM memory. Windows OSHI performance-counter warnings are host diagnostics, not a CQuests exception.

## Remaining live checks

No arbitrary-engine/version guarantee or large-server performance benchmark is implied. Purpur, Canvas, other forks, Bedrock/Geyser rendering, very old clients through protocol translators, actual player skins and custom formatted names need a staging/client check. Native dialogs require a capable server/client combination; the compatible view remains available through the legacy conversation setting.

Your custom economy and shop plugins were not supplied. Verify a real paid upgrade, quest reward command and any shop that directly modifies inventories on staging. The tests used an isolated economy fixture. Normal player command and inventory transfer paths are guarded; third-party APIs can bypass ordinary inventory events.

Tested work is bounded to one crop per hit and one NPC search at a time per scatter job; it does not scan an entire selected farm or generate a whole 10k square. No full-population load profile, 360-hour playthrough or completion-time guarantee was performed. Farming areas must be configured in your own world using `INSTALL-1.2.md`. Chat buffering covers normal player chat, not every system packet from other plugins.
