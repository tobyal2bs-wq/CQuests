# CQuests 1.3.3: readable NPC nameplates and dialogue pacing

Quest NPCs use separate chapter-filtered TextDisplay nameplates. The default layout is an uppercase gold name above an aqua level on its own line. The legacy shipped white/gray one-line format upgrades in memory; custom name formats remain intact. Existing NPC IDs and saved names are unchanged. `npc.uppercase-names: false` preserves original display case.

During overhead dialogue the nameplate rises from 2.45 to 3.85 blocks above the saved NPC position; private speech remains at 2.15 blocks. The built-in entity name is removed to avoid a duplicate tag when aiming at the NPC. Nameplates follow the NPC's normal chapter visibility, despawn and reload lifecycle. Concurrent conversations keep the nameplate raised until all sessions finish. Mannequins retain their skin profile and have the redundant default description cleared.

Typing defaults to one character every two ticks. Every sentence, including the last, remains visible for an additional 80 ticks (four seconds at 20 TPS) before the next sentence or continuation prompt. Configure `dialogue.character-ticks` (1-10) and `dialogue.reading-pause-ticks` (20-400) in config.yml. Missing settings on existing installations use the new defaults. Long sentences wrap into bounded, Unicode-safe chunks so text cannot grow into the lifted nameplate. Sounds are emitted only with character updates.

## Validation

Java 21 build with 73 tests passed. New tests verify timing bounds, Unicode chunk boundaries, uppercase styling/punctuation and concurrent conversation reference tracking. Local JAR SHA256: `452b19d104a8ae069cbb7359d08489a4912aec31e940fa0b3c0d02d5caa0aa15`.

The Paper/Folia 26.2 protocol-client matrix checks actual uppercase two-line nameplate text, raised display position, absence of the built-in duplicate name and lowering after speech stops. It repeats private progressive speech, native and legacy dialogue/claim handling, custom XP, WorldGuard mature-wheat harvesting, merchant route/facing, OP editor checks, duplicate trade packets and isolated demo checks. Separate restarts verify merchant persistence and route-ticket cleanup. Release manifests identify the exact local test JAR and/or unchanged CI build artifact.

Protocol verification checks server state and client packets; it does not replace a human visual/sound check or prove arbitrary plugin/fork combinations. Actual paid upgrades still need staging with the custom Vault economy.

## Install and farm testing

Stop the server, back up the CQuests folder and replace the old JAR with CQuests-1.3.3.jar. Keep existing player data and quest/NPC configurations. Roll back with the previous JAR and matching backup. No player progress reset is included.

See `FARM-TESTING.md` for WorldEdit/WorldGuard selection, farm outline saving, Survival-mode harvesting, personal hoe handling and upgrade-anvil setup. Farming behavior is unchanged by this release.
