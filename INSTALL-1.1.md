# CQuests 1.1.0

This continues Claude's commit 4a1ca94. The five-chapter story, quest IDs, existing villagers, deterministic quest seed, currency rules, anti-abuse rules and player progress remain intact.

## Upgrade

1. Stop the server and back up the old plugin JAR and entire plugins/CQuests folder.
2. Replace only the old CQuests JAR with CQuests-1.1.0.jar. Keep exactly one CQuests JAR.
3. Start the server normally. Do not replace your players, spawns, quests or generator files with defaults.
4. The first start adds eight missing side villagers to npcs.yml. Existing NPC definitions are retained, with npcs.yml.before-1.1.0 saved before changes. A .content-1.1.0 marker prevents repeated upgrades.
5. Existing configuration and custom text stay in place. New options use the new defaults when absent. Existing explicit settings still apply; in particular set spawning.roam-minutes to 0 if your older config has 20 and you want scattered villagers to stay still.
6. Use /cq npc list to see placed and currently spawned counts. NPC entities exist only near players. Use /cq npc tp stephan to visit a saved spot. Unsafe old points produce a warning; /cq npc repair stephan searches nearby, or /cq npc place stephan validates your current spot.

The boss bar defaults off even when the old config has tracker.enabled: true. That option controls availability; tracker.default-on: false controls the initial player preference. Taking a quest never enables it automatically.

## Player commands

    /quests                       book journal by default
    /quests book                  journal book
    /quests menu                  chest journal with settings buttons
    /quests settings              same settings menu
    /quests mode book             book journal and NPC conversations
    /quests mode menu             chest journal and NPC conversations
    /quests mode chat             chat list and original timed NPC speech
    /quests track                 boss bar on/off
    /quests directions            arrow and villager distance on/off
    /quests achievements          earned milestones and next targets

Menu mode is recommended for touch/Bedrock clients whose book command links are unavailable. Changes apply next time you speak to the villager. NPC actions remain usable without quests.use; the journal, tracking and other player commands retain that permission requirement.

Conversations have bounded pages, a quest/reward preview and explicit response buttons. Accepting or claiming rewards checks the current offer, expiry, player, NPC visibility and distance again. Closing the conversation does not claim the pending reward. Chat mode retains the original second-click acceptance.

The high-contrast boss bar uses white text and a white progress bar, with green when ready to return. Single TALK objectives omit 0/1 clutter. Directions use a separate action bar, show an arrow relative to the player's facing and distance in meters, and name the other world instead of giving a misleading cross-world arrow.

## Scatter by chapter or selected NPCs

    /cq scatterworld chapter1 10000 10000 world
    /cq scatterworld chapter2 10000 10000 world 12000 0
    /cq scatterworld chapter3 10000 10000 world_nether
    /cq scatterworld chapter5 10000 10000 world_the_end
    /cq scatterworld B.O.B 2000 2000 world
    /cq scatter chapter4

Width and depth are full dimensions, not radius. Without coordinates, the rectangle centers on that world's spawn. Width/depth are bounded to 16–100000 blocks. Existing /cq pos1, /cq pos2 and WorldGuard scattering remain available.

chapterN selects villagers first introduced in that chapter. An NPC used across several chapters belongs to its earliest chapter, so scattering a later chapter does not silently move an earlier shared villager. Repeat scattering whenever you want; it edits NPC positions and roaming areas only, never player progress. Individual selectors accept case-insensitive IDs or unambiguous display names, including B.O.B.

Terrain searches run one NPC at a time with at most 32 attempts per NPC, loading only candidate chunks. Large rectangles can generate new chunks and take time. Completion reports placed and skipped counts. A failed search keeps the old position; a newer edit or reload invalidates older pending placement work.

All placement routes require a safe full floor and two clear blocks above it. End placement checks every column in a circular 10-block radius for supporting terrain within four blocks of the central floor; it rejects void edges, holes and large drops. Nether placement rejects lava within 10 horizontal blocks near the standing height and locations at or above y=123. It does not use the Nether roof or an unchecked highest-block fallback. Region-owned chunk snapshots are used for the surrounding terrain.

Spawns save atomically with a previous-copy backup. Removing an NPC is remembered across restarts; explicit placement/scattering enables it again. Scattered NPCs stay put by default. Older configs can retain roaming until spawning.roam-minutes is set to 0.

## Progression and new content

- Future-chapter villagers remain hidden until their first chapter, including previously met NPCs. Active quest participants remain visible. Shared villagers unlock from their earliest story appearance.
- Story progression no longer requires a quota of side jobs. To restore that rule, set quests.require-side-quests: true; existing per-quest side-required numbers then apply.
- Eight additional side-job villagers: Luma, Copper Jack, M.A.P., Fern Greenbough, Nox, Ember, Astra and Tilly Weaver.
- Existing villagers remain available for optional side work. With hide-finished-villagers enabled, they disappear only when their optional side work is also exhausted and no active quest needs them.
- Fourteen new milestones cover side jobs, daily jobs and meeting villagers, alongside the original chapter and ending achievements. They have a separate Wanderers advancement root. Milestones use existing saved counters, so earned progress is recognized on join.
- Protection remains active, with a quiet message and no boundary particles.
- /cq npc rename bob B.O.B changes the display name while keeping the internal ID and all progress.

## Rollback

Stop the server, restore the old JAR and the plugins/CQuests backup taken before the upgrade, then start normally. Restoring the whole folder returns both configuration and progress to that backup's time. To keep later player progress while rolling back the JAR, retain the players directory; the added preferences are extra YAML keys ignored by the old build. Also restore the old npcs.yml and spawns.yml together if you want the exact previous roster/positions.

Do not use /cq player reset for an upgrade or scatter. No reset is required.

## Verification

The delivered validation report records checks actually run. Unit tests cover terrain boundaries, liquid/roof rejection, chapter visibility, preserved IDs, display-name lookup, pagination and preference persistence. The isolated Paper protocol test exercises real NPC spawns, dialogue menu hand-in/acceptance, tracker opt-in, arrow/distance output, protected menu inventory, repeated scattering and restart persistence.

A protocol test does not verify the final appearance in a graphical Minecraft client, Geyser/Bedrock rendering, a hosted economy plugin or your server's plugin combination. Review those on a staging copy before replacing a live server.
