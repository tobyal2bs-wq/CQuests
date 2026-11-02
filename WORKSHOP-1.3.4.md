# Fieldsmith and conversation update

Right-click the registered upgrade anvil to open the Fieldsmith. Your current hoe is on the left and its next upgrade is on the right. Hover over the next hoe for its XP multiplier, extra-wheat chance, hit interval, required Wayfarer level and price. Click that hoe or **Review upgrade**, then click **Buy** to purchase it.

The workshop checks your saved tier, level and Vault payment when you buy. Reviewing an upgrade costs nothing. After buying, repeated clicks on the old Buy slot cannot purchase another tier: select the next hoe explicitly to review it. The locker button collects your personal hoe inside the fields; outside, it tells you where to collect it.

An administrator binds the anvil once: look at it and run `/cq farm anvil`. Players then right-click it; they do not need commands. `/cq farm menu` remains an administrator preview. Farm outlines and WorldGuard setup are unchanged; see [FARM-TESTING.md](FARM-TESTING.md).

Conversation replies now read like responses to the NPC. Quest offers show their title, level and rewards on separate lines. The compatible inventory dialogue shows an unavailable response button until its final page, and its book button opens the book directly. Native dialogue keeps a clear reply and leave option. Existing quest checks, private overhead typing, sentence reading pauses and rewards remain in place.

Install by stopping the server, replacing the CQuests JAR, and keeping its data folder. No quest, NPC or progression data needs resetting. Use the server's real Vault economy on a staging server to check purchases before opening to players.
