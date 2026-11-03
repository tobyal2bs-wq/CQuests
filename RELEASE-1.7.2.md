# CQuests 1.7.2

Makes the wheat farm work the way people expect. Just replace the jar.

## How the farm works

1. `/cq farm wand <name>` gives you the outline stick. Left-click the corners of your field in order (right-click undoes a point).
2. `/cq farm save <name> <worldguard-region>` saves it. **Nothing happens until you save**, and the field must sit inside an existing WorldGuard region.
3. Players walking into the field get their farm hoe in the hotbar. They harvest by **left-clicking fully grown wheat with it in survival mode**. The wheat gives XP and wheat items and grows back after a second.
4. Better hoes are bought at the Fieldsmith Anvil (`/cq farm anvil` gives you one to place).

## Fixed

* **Wheat in a saved field just broke like normal wheat.** Now only the farm hoe can harvest it there. Breaking wheat or farmland any other way is blocked, with a hint on the action bar telling you what to do. Admins in creative mode can still edit the field.
* **New players had no hoe.** The first hoe (Fieldhand I) is free but had to be "bought" at the anvil first, so new players walked in empty-handed. It is now given automatically the first time they walk into a field.
* **Creative mode did nothing.** Harvesting only works in survival. Creative players with the hoe now get a hint instead of silence.
* The save message now explains how players harvest.

Tested on Paper 1.21.4, the newest Paper and the newest Folia. The JAR attached to the release is the exact file built and tested in that run.
