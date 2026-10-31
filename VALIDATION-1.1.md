# CQuests 1.1.0 validation — 2026-10-31

Continued from Claude's commit 4a1ca9404bbf21c17c2adb8326e7dd56eb500216.

## Build and preservation

- Gradle 8.14.3 build completed on Temurin Java 21. All 21 JUnit tests passed, with zero failures/errors.
- Every plugin class is Java 21 bytecode (major 65); plugin metadata is version 1.1.0.
- JAR SHA256: cffea3506b389f490d1618830dde1bfbb237f50dbf7d451c0d6ebfc2b383f582
- All 101 original NPC definitions were compared structurally against the supplied ZIP and remain unchanged. Eight side villagers are added, for 109 total.
- quests.yml and generator.yml retain the original bytes apart from checkout newline normalization. Story IDs, objectives, rewards and deterministic seed are preserved.
- Regenerating the story from tools/story produces equivalent NPC and quest data, including all eight additions.

## Real isolated server tests

The final JAR was run on Paper 1.21.4 build 232 and Folia 1.21.4 build 6, with two complete boots each. Folia used two region tick threads. A Mineflayer protocol client connected to each server.

Both servers passed:

- Startup, NPC loading/spawning, 109 saved NPC positions and 21 registered advancements.
- Boss bar absent by default, including after accepting another quest.
- Book journal default; book response button completes the welcome quest.
- Replaying that response does not pay/complete the quest twice.
- Chapter-five Astra hidden from a chapter-one player.
- Chest dialogue opens, displays paginated text and accepts The Wanderers through its explicit button.
- Opt-in boss bar and live arrow/distance output.
- Menu inventory rejects attempts to take display items.
- World scattering in a 10000 × 10000 area (one selected NPC), then scattering the same NPC again in a 64 × 64 area, without losing the active story.
- Backup command, plugin reload, shutdown saves and a full restart.
- Tracker, directions and menu preferences survive restart; seeded legacy progress remains intact.
- Upgrading the original NPC file keeps every original definition and adds exactly eight villagers.
- No CQuests stack traces occurred in the final runs.

Paper additionally passed real terrain fixtures in separate dimensions:

- A supported End platform accepts placement.
- Removing one supporting column exactly ten blocks away rejects the new placement and keeps the previous position.
- Nearby Nether lava rejects placement; replacing it with safe ground permits placement.
- Nether roof placement is rejected.

Terrain boundary cases, height limits, liquid floors, negative coordinates, dialogue pagination, case/punctuation lookup and saved preferences are also covered by unit tests. Folia exercises region-scheduled placement/search, dialogue, tracking, scattering and restart; its vanilla terrain-editing commands were excluded from the fixture test.

## Limits

These were local servers and a protocol client. Graphical Java/Bedrock appearance, Geyser/Floodgate interaction, WorldGuard combinations, a hosted economy provider, other Paper/Folia versions and the user's live server have not been verified. Currency-command invocation is exercised without a real economy plugin; actual account credits are not confirmed.

Fresh flat-world setup emitted the server's own generator warning about missing layers during the initial fixture setup. It was not a CQuests exception. No live worlds, player data or hosted services were modified.

See INSTALL-1.1.md for installation, commands and rollback.
