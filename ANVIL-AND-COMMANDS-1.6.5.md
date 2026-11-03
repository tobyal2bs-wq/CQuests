# CQuests 1.6.5

The player entry points are `/quests` for quests and `/quest mail` for mail. No new standalone player commands were added. Quest home no longer includes Mail or Farming, and mail no longer links into quest home. Quest-specific tracker/direction settings remain with quests.

Hoe upgrades are a physical workshop:

1. As OP, run `/cq farm anvil`. It gives a named, marked **Fieldsmith Anvil** item.
2. Place it on solid ground. The location is saved; multiple workshops are supported.
3. Players right-click that anvil to open the custom hoe-upgrade GUI. No player command opens this GUI. Ordinary anvils keep their vanilla behaviour.

The anvil command and marked-item placement require actual OP status. Having the admin permission alone is insufficient. Non-OP players cannot break registered workshop anvils; explosion and falling-block changes are blocked for those stations. OPs can break them to remove their registration. Breaking one drops the normal block rather than recreating a marked workshop item; use the OP command to create another workshop.

Players must remain within six blocks of the workshop to use its inventory. Each click checks the saved station and distance, including before a purchase. Existing exact prices, sequential tier checks, inventory protection and purchase replay guards are retained. NPC farm roles point players to the anvil instead of opening upgrades remotely.

Existing single-anvil bindings in `farming.yml` are retained. `/cq farm bind` lets an OP register an existing anvil; the former `/cq farm anvil` look-to-bind behaviour is now under this command. Old `/quests farm` and `/cq farm menu` calls only explain how to find/create the anvil.

Keep the data folder and replace the JAR while stopped. Mail, quest progress, tool tiers and existing player settings are preserved. Command aliases and internal dialogue subcommands remain for compatibility, but normal use needs only `/quests` and `/quest mail`.
