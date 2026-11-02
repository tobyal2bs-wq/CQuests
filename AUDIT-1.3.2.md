# CQuests 1.3.2: temporary merchant demo

`/cq merchant test [rowan|brann|mira|sable|orin]` creates an OP-only private demo on flat outdoor ground. It starts two blocks in front of the operator, walks six blocks using native pathfinding, then accepts a right-click to preview that merchant's trades. No world blocks are changed. `/cq merchant test stop` removes the demo; it also expires after two minutes or disappears on logout/reload/shutdown. Starting another demo replaces the previous one. At most four demos run concurrently.

Demo definitions live only in memory and are excluded from the saved merchant list. Direct trade and offer-save calls reject demos; the preview GUI cannot transfer items or charge money. Losing OP prevents further access. The demo uses the existing terrain checks, entity scheduling and bounded route chunk tickets. Operators should use flat, unobstructed outdoor ground; unsafe positions are refused and blocked paths stop normally.

Real merchant timing is unchanged: configure spawn/trail/end, then `end` or `walk` starts it. Trading opens on arrival. Enabled merchants repeat the walk after restart/reload. Unconfigured default presets do not spawn themselves.

## Validation

- Java 21 build and 69 unit tests passed, including denial of the test command to a non-OP with admin permission.
- Final local JAR SHA256: `ab289eeceb67d3c134b36efa20c2c423aa84370d9b1725ee294e46cab7b38330`.
- Real Paper and Folia 26.2 fixtures with protocol clients: demo walks, owner opens its inventory and confirms a preview; direct reward/offer-save attempts fail; inventory and balance remain unchanged; another observer receives no demo metadata; stop removes the temporary definition. Saved `merchants.yml` remains byte-identical across the demo.
- The same matrix repeats native/legacy dialogue, progressive private overhead speech, custom XP without vanilla-XP changes, WorldGuard farming/protection, merchant trail/facing, OP editor checks and duplicate claim/trade packet regressions.
- Separate full restarts preserve the configured real merchant route, enabled state, trade templates and prices. Disabling a real merchant releases route tickets.

Tests use a validation-only Vault provider, not the actual custom economy. Protocol tests do not visually inspect a Minecraft client and cannot prove every server fork or third-party plugin combination. The exact tested JAR hashes and runtime matrices are included in the release manifest; CI results are linked there too.

Stop the server, back up CQuests data and replace only the old JAR with `CQuests-1.3.2.jar`. Keep the existing data folder. Existing quests, rewards, NPC IDs and player progress are preserved. Roll back using the previous JAR and matching backup. See `MERCHANTS-1.3.md` for setup.
