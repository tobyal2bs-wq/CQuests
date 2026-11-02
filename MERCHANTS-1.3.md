# CQuests 1.3: story twists and travelling merchants

Five merchants are supplied in `merchants.yml`. None spawns until an operator configures its locations and starts its walk. Existing quest/NPC files and player progress remain in place.

## Place a merchant

Only a player whose server OP status is true can use these editor actions. Granting `cquests.admin`, `cquests.bypass` or a permission wildcard to a non-OP does not authorize merchant editing.

1. Stand on safe outdoor ground: `/cq merchant spawn rowan`.
2. Run `/cq merchant wand rowan`. Right-click ground blocks in order to mark the trail; left-click to undo. Gold floor blocks are a private preview, not real world edits or obtainable blocks. Wait for each saved-point message.
3. Stand at the store, look in the direction the merchant should face, and run `/cq merchant end rowan`. This saves the endpoint and facing, clears the preview and starts walking. The store may have a roof.
4. The villager walks through the trail in order, then faces your saved direction and opens trading. It never teleports between waypoints. `/cq merchant walk rowan` restarts an existing route. Manual `/cq merchant point rowan` and `/cq merchant shop rowan` remain supported.

Use `/cq merchant list` for the five IDs: `rowan`, `brann`, `mira`, `sable`, `orin`. Repeat the setup for each merchant. Routes must stay in one world, with at most 64 waypoints and a maximum 32-block gap between successive stops. Floors, headroom, world borders, End support and Nether lava rules are checked. Spawn points use the outdoor NPC rules; store/waypoints allow roofs.

`/cq merchant undo <id>` removes the last waypoint. `/cq merchant routeclear <id>` clears waypoints. Changing any location stops the current merchant until `/cq merchant walk <id>` is run again. `/cq merchant despawn <id>` disables it while retaining trades and locations. Enabled merchants start their route again after restart/reload. Trail previews expire after two minutes and clear when you finish or leave. They do not modify WorldGuard regions, grant build access or create drops.

Movement uses native pathfinding, not repeated teleports. Build a walkable route with sensible stairs and doors; a blocked stop closes trading and reports the route as blocked. Active routes retain plugin chunk tickets so merchants survive when no player is nearby. Routes are capped at 128 distinct chunks each; keep them short to limit memory use. Shared chunks are reference counted, and disabling/replacing a merchant releases its tickets. Five default merchants each use one ten-tick entity task. Shops remain frozen on arrival.

## Edit offers

An OP crouch-right-clicks the villager, or uses `/cq merchant edit <id>`. Normal players right-click to trade after arrival. Crouching as a non-OP never grants editor access.

- Select one of seven offer tabs along the top.
- Click the first cost, second cost or reward field, then click a stack in your own inventory. Its amount and complete item metadata are copied. Sample items remain yours.
- Right-click an item field to clear it. The second item cost is optional.
- Click the gold-ingot money field, then use the +/- buttons. Money price zero means item-only barter. A money-only offer is also supported; an offer must have at least one cost and a reward.
- Adjust a selected item's quantity with the same buttons, within its legal stack limit.
- Save the selected offer, or delete it. Switching tabs or closing discards unsaved changes.

Ghost slots are never storage: shift-click, number keys, offhand swaps, dragging, double-click collection and creative inventory actions cannot extract GUI items. The server rechecks OP status at capture/save time, so losing OP with an editor open does not retain editing rights. Concurrent edits reject stale revisions instead of overwriting another operator's changes.

Player trades use a review/confirm step and process one exchange per confirmation. Costs match full item metadata, including name, enchantments and damage. Only the player's ordinary storage/hotbar slots pay costs; offhand and armor are not payment slots. Both item costs are simulated together with reward capacity before inventory changes or money withdrawal. A full bag or missing cost declines the whole exchange. Rewards are not dropped on the ground.

Money uses the registered Vault economy's exact balance/withdrawal API, including the custom economy already used for farm upgrades. Missing/declined providers fail closed for paid trades. A normal failed inventory commit attempts to restore inventory and refund through the same provider. Cross-plugin money and Minecraft inventory saves are not a power-failure atomic transaction; stage-test your actual provider and shops. Operators set the economy balance of offers, and should avoid profitable trade loops or incompatible external sell prices.

Bound farm tools, editor wands, bundles and inventory-containing item templates are refused as costs/rewards. This avoids minting personal tools or hiding them inside container rewards. Arbitrary third-party plugins that bypass Bukkit events or directly alter inventories remain outside the GUI's security boundary.

## Example trades supplied

| Merchant | Give | Receive |
|---|---|---|
| Rowan, provisioner | 32 wheat | 8 cooked beef |
| Brann, forgehand | 32 raw iron + 8 coal | 24 iron ingots |
| Mira, wayfinder | 8 paper + 1 compass | 1 empty map |
| Sable, salvager | 32 rotten flesh | 4 leather |
| Orin, deep delver | 16 amethyst shards + 8 copper ingots | 8 glow ink sacs |

Each has a second example offer. All example money prices start at zero; set any price in the editor. These are editable starting suggestions, not a guarantee of compatibility with every server economy.

## Story twists

`twists.yml` adds foreshadowing and completion reveals to Lucy, Ned, Hugo, Quill and Esme, with a final payoff when returning to Stephan after Aldric's quest. A hidden route, a deliberately planted message and the true purpose of the five keys link the chapters. The original objectives, requirements, levels, rewards, quest IDs and generator seed are preserved. Players already on quests keep their progress; completed quests do not replay themselves.

Completion reveals only appear through the existing ready-to-turn-in dialogue flow. Set `enabled: false` in `twists.yml` and `/cq reload` to disable additions. Editing that file customizes the new story without overwriting your original `quests.yml`.

## Update and rollback

Stop the server and back up CQuests data/worlds. Replace the old JAR with `CQuests-1.3.1.jar`, keep your existing folder, then start normally. Missing `merchants.yml` and `twists.yml` are added. Merchant edits use queued atomic file replacement, drained on shutdown. Back up these two files alongside your other configurations. Rolling back requires the prior JAR and matching backup; older versions ignore merchant definitions and twist additions.

## Player skins for quest NPCs

As an OP, use `/cq npc skin stephan Notch` (replace Notch with a valid Minecraft username). `/cq npc skin stephan default` uses the default player appearance; `/cq npc skin stephan villager` restores the villager. The existing `player-skin` setting in `npcs.yml` is also supported. These are native mannequin NPCs on Minecraft 1.21.9+; older servers fall back to villagers. Client skin loading depends on its access to Minecraft skin services. NPC names, chapter visibility, dialogue and quest IDs remain the same.
