# CQuests 1.2.3 follow-up audit

Continues the existing architecture and the 1.2.2 audit. Story/NPC IDs, configuration defaults, generator seed and grind balance are unchanged. No proposed engagement features were added.

## Fixed

- Offhand block interactions previously returned before the farm's container restriction. Both hands now pass through tool/container guards. Wand edits, workshop opening and harvesting remain main-hand actions, preventing duplicate harvest calls.
- Pushing a placed block with a piston previously left its quest-protection mark at the old position. Marks now follow extension and retraction. Source states are captured before destinations are written, so overlapping chains and chunk boundaries retain the correct marks. Naturally occurring blocks do not inherit a neighbor's mark, and blocks destroyed by a piston do not transfer one. Cancelled piston events are ignored; placement-count history stays attached to locations.
- Incoming chat previously removed a conversation viewer before checking the 64-message limit, silently dropping overflow. A concurrent arrival during the final flush could also remain hidden until another click. Deferral and resuming now share one synchronized buffer decision. Overflow remains live instead of disappearing. Late arrivals after resuming also remain live. ArrayDeque gives constant-time size checks and removes the previous linked-queue traversal.
- Natural dry-soil decay during the one-second air gap could turn the farmland under a pending crop into dirt, preventing regrowth. Only farmland directly below a pending crop is protected from natural fading. Ordinary farmland keeps its normal behavior.

The piston movement direction follows the server's event construction for both push and pull, as shown in [Paper's implementation](https://github.com/PaperMC/Paper/blob/ver/1.21.4/paper-server/patches/sources/net/minecraft/world/level/block/piston/PistonBaseBlock.java.patch).

## Checks

- Gradle build and 52 unit tests, including 200 concurrent chat arrival/resume races, buffer overflow, offhand container clicks, offhand harvest suppression, temporary soil protection, piston chains across chunks, natural-block separation and destroyed-block handling.
- Isolated Paper 26.2 build 135 and Folia 26.2 build 7 with actual WorldGuard, WorldEdit, Vault provider, PlaceholderAPI and ViaVersion/ViaBackwards. The protocol-client matrix covers existing farm transactions, regrowth, native dialogs, private speech and legacy book fallback. Additional runtime probes check the offhand handler against a real chest and move a tracked block with a real powered sticky piston in both directions.
- GitHub Actions checks the exact published commit separately: build, Paper 1.21.4, latest Paper and latest Folia. Use the release manifest's run link to confirm its result.

## Limits and install

Overflowing the bounded chat queue deliberately allows excess messages through while speech continues; chat is not silently discarded to preserve a visual pause. Only normal player chat events are buffered, not every third-party system packet. The concurrency test validates the buffering decision, while client tests validate packets rather than graphical appearance.

This update does not establish universal exploit-free or lag-free behavior. Third-party plugins that modify inventories/worlds directly, the custom economy provider, crash-time cross-plugin transactions, proxy-only translation and large-player-count performance retain the limits described in the previous audit. Piston tracking covers Bukkit piston events; it does not infer arbitrary third-party block movement or convert every block transformation into persistent provenance.

Stop the server, back up CQuests data and worlds, replace the old JAR with `CQuests-1.2.3.jar`, keep existing data/configuration, and start normally. Do not leave multiple CQuests JARs installed. Rollback uses the previous JAR and matching backups.
