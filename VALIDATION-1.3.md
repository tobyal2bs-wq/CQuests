# CQuests 1.3.0 validation

## Build and automated checks

- Java 21 target; `gradlew build` completed with 67 passing unit tests.
- New tests cover overlapping item costs, full-inventory rejection, exact item metadata, legal stack capacity, immutable trade templates, OP-only administration and modern crouch input.
- Story comparison verifies all 101 quest definitions retain their original objectives, requirements, levels, rewards and ordering with twists enabled or disabled.
- Original `quests.yml`, `npcs.yml` and `generator.yml` are unchanged from 1.2.3.

## Local server and protocol-client checks

Final JAR SHA256: `156d1c91dbe60c62304671cbfb9dd9a8118cfbd262fdd0b1f25c2df9a983ce0f`.

Real Paper 26.2 build 135 and Folia 26.2 build 7 fixtures, with WorldGuard/WorldEdit, PlaceholderAPI, Vault and ViaVersion/ViaBackwards. A validation-only Vault provider records exact withdrawals; it is not included in the shipped JAR.

- Native dialogue flow, private speech displays, quest claiming, farming upgrades, mature-wheat harvesting through a build-deny region, level feedback and existing protection/piston regression checks.
- Real client route placement, villager walking and arrival before trading opens.
- OP crouch-click editor, copying two item costs and a reward without moving sample items, and saving a $100 price.
- Non-OP with `cquests.admin` still denied editor mutation, merchant commands and a copied route wand. Losing OP while the editor is open closes access.
- Reviewed trade removes both costs and exactly $100, then awards the requested reward once.
- Full inventory, insufficient balance and stale revision failures preserve costs and balance.
- Older 1.21.4 protocol client receives the book fallback and can claim a quest.
- Separate full shutdown/start checks preserve merchant coordinates, waypoint, enabled state, exact item templates and money price; the merchant automatically walks back to its store on both engines.

The test harness and validation plugins stay outside production source and release JARs. Machine-readable evidence is included in the release manifest.

## Limits

Protocol clients do not verify graphical appearance, sounds as heard by a human, arbitrary server forks or every Minecraft release. CI separately runs its committed server smoke-test matrix. Stage-test the actual custom Vault economy, permissions plugins and external sell/shop plugins before enabling paid trades. Server power loss during a cross-plugin money/inventory commit is not an atomic transaction. Route tickets are bounded to 128 distinct chunks per merchant; route length and terrain still affect memory and native pathfinding cost.

See `MERCHANTS-1.3.md` for setup, security boundaries and update/rollback instructions. Existing player progress is retained; no data reset is part of installation.
