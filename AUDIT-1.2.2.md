# CQuests 1.2.2 audit

This update hardens the existing plugin. Quest/NPC IDs, story text, generator seed, progression balance and existing player settings are preserved. No proposed engagement features were implemented.

## Corrections

- Reconnecting before a queued quit save finishes reuses the current player ledger. The old session cannot overwrite a newer session or a restored backup. Offline ledgers are evicted only after their latest snapshot has been written.
- Bound hoes cannot move through offhand inventory swaps or hopper transfers. Armor-stand/item-frame interaction is blocked while a tool is carried, including during exit cleanup. Quest deliveries ignore bound tools, preventing a reusable locker tool from satisfying item hand-ins repeatedly.
- Completion rechecks objective readiness at the reward boundary. Already removed/completed quests remain unable to pay twice. Craft clicks with no successful inventory action no longer advance objectives.
- Harvesting rejects creative/spectator mode, disconnected players, another world and targets beyond six blocks from the player's eye. Existing ownership, level/tier, WorldGuard, polygon, mature-wheat, cooldown and pending-crop checks remain enforced.
- Placed-block and counted-placement marks now live in compact chunk persistent-data bitsets. Restarting no longer clears new marks, and there is no global tracking cap that clears protection. Marks recorded by older versions cannot be recovered retroactively. These marks follow ordinary chunk saving; third-party world edits and movement of blocks are not a complete provenance system.
- Achievement reset revokes the actual `wayfarer_*` advancements.
- The workshop disables confirmation for owned tiers, skipped tiers and unmet level requirements. Purchases still recheck eligibility and successful Vault withdrawal.
- Native dialogs check local ViaVersion's client protocol. Older clients receive the existing book/menu fallback. Bedrock retains its fallback. A proxy-only translator without local ViaVersion cannot be detected by this bridge.

## Performance

Movement checks handle entry and exit immediately, but no longer rescan the full inventory for every block walked. Full audits remain on join, farm entry and the existing ten-tick timer. Empty farms and locations outside candidate bounds avoid WorldGuard reflection. Block history uses chunk data instead of a server-wide map of position objects.

## Validation

The Gradle build and all 44 unit tests pass, including regressions for reconnect/save ordering, stale reward responses, item transfers, delivery filtering, harvest reach, creative-mode farming, failed crafting, chunk-backed placement marks and achievement reset.

The runtime matrix uses isolated Paper 26.2 build 135 and Folia 26.2 build 7 with WorldGuard/WorldEdit, PlaceholderAPI, a validation-only Vault provider, and ViaVersion/ViaBackwards. It exercises single-crop harvesting through WorldGuard build denial, duplicate-hit suppression, tier/level gates, one debit per upgrade, personal locker restoration, regrowth, custom XP, native dialog responses and private speech. A separate 1.21.4 protocol client checks book fallback on those modern servers. Final results are recorded with the release manifest; client packet tests do not establish graphical client appearance.

The existing GitHub Actions matrix additionally checks Paper 1.21.4 and latest Paper/Folia startup, NPC placement, reload, backups and restore. Its result must be checked on the commit being installed.

## Remaining practical limits

This is not a claim that every possible plugin combination is exploit-free or lag-free. Test the actual custom economy and shop plugins in staging: the local Vault provider verifies CQuests' debit handling, not your provider's implementation. Plugins that directly rewrite inventories can bypass normal Bukkit inventory events. Cross-plugin rewards and queued saves are not one atomic transaction, so abrupt process/power failure can still roll back recent state. Persistent block marks likewise follow normal chunk-save durability. No large-player-count load test or graphical Java/Bedrock session was performed in this audit.

## Install

Stop the server, back up the CQuests folder and worlds, replace the old CQuests JAR with `CQuests-1.2.2.jar`, then start normally. Keep the existing data/configuration folder. Do not leave multiple CQuests JARs in `plugins/` or use a plugin hot-loader. Rollback requires the previous JAR and matching backups. Chunk marks added by this version are namespaced CQuests data and are ignored by older versions.
