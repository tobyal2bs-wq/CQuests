# CQuests 1.3.1 audit and validation

## Changes

- Merchant setup: `/cq merchant spawn <id>`, `/cq merchant wand <id>`, right-click the ground in trail order, then `/cq merchant end <id>` while facing the store direction. End saves the endpoint/yaw and starts the walk automatically. Left-click with the wand undoes a point.
- The trail uses private temporary gold floor markers. It does not place real blocks, drop items or bypass WorldGuard build protection. End/quit/reload clear previews; they expire after two minutes.
- Native pathfinding follows waypoints in order; no teleport is used between trail points. Arrival applies saved yaw before opening trading.
- `/cq npc skin <id> <username|default|villager>` gives OPs an in-game appearance setting. Native mannequins are supported on Minecraft 1.21.9+; older servers keep the villager fallback.
- Locked GUIs accept at most one queued top-slot callback per player. Editor sample capture is bounded separately, and execution rechecks the current holder and OP status.
- Quest NPC clicks validate the live entity, distance and chapter visibility before interaction. Both interact packet variants are handled with a shared debounce. NPCs cannot be picked up by boats/minecarts. Modern crouch input is used for farm NPC roles too.
- Existing quest objectives, NPC IDs, generated quest seed, rewards and player progression are preserved.

## Evidence

`gradlew build` passed with 68 unit tests. The new queue regression sends 1,000 GUI click events, verifies one scheduled callback, verifies normal input resumes after execution, and rejects callbacks for a replaced inventory holder.

Final production JAR SHA256: `f413d429927a118037a96b283ffb5ba00612f79d4ddd46dfcfef12f43ef76082`.

Local real-server matrix: Paper 26.2 build 135 and Folia 26.2 build 7, with WorldGuard, Vault, PlaceholderAPI and ViaVersion/ViaBackwards. A 26.1 protocol client exercises:

- Actual wand right-click selection, private gold marker reception, marker restoration after end, automatic walking and saved 135-degree arrival facing.
- OP trade editing, unchanged sample inventory, losing OP with the editor open, and non-OP command/wand/direct-service mutation attempts.
- Replaying the confirmation packet 20 times still produces one trade, one money debit and one reward. Full bags, insufficient funds and stale offer revisions preserve payment items and balance.
- Repeated dialogue claim commands still produce one quest claim. Per-viewer overhead speech remains private, native dialogs open, custom farming XP levels advance without changing vanilla XP, and existing WorldGuard harvest/protection/piston regressions pass.
- A named player profile is applied to an actual native mannequin quest NPC. This verifies the server profile API, not human-visible skin texture downloads.
- A 1.21.4 protocol client receives the book fallback and completes a claim.

Separate shutdown/start checks verify saved prices/templates, route, enabled state and automatic walking. Disabling a merchant releases all route tickets; walking can restart afterwards. See the release manifest for exact JAR hashes and matrix results, and the linked commit's GitHub Actions run for build/server smoke tests.

## Limits and installation

These checks cover the reproduced packet bursts and ordinary failures; they are not a guarantee against every third-party plugin, hostile packet sequence, crash or economy-provider failure. A validation-only Vault provider was used. Stage-test paid trades with the actual custom economy and external sell plugins. Protocol tests do not visually inspect the Minecraft client or prove arbitrary versions/forks.

Stop the server, back up its CQuests data, replace the old JAR with `CQuests-1.3.1.jar`, keep the existing data folder, then start normally. Do not reset player data or replace customized quest files. Roll back with the previous JAR and matching backup. Setup details are in `MERCHANTS-1.3.md`.
