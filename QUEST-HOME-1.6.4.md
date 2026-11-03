# CQuests 1.6.4 — a clear starting point

`/quests` now opens **Quest home** instead of the multi-page book. It shows the current Wayfarer level and next story quest, with large buttons:

- **What should I do?** shows the next objective or explains the level/previous-task requirement.
- **My quests** lists only active quests. Choose one to see its tasks and progress.
- **Mail** opens the dialogue inbox.
- **Farming & tools** explains harvesting and links to hoe upgrades.
- **Settings** contains the quest tracker and direction switches.
- **Close** returns to the game.

Quest details have Back to my quests and Back to quest home. Mail and the hoe-upgrade inventory also link back to quest home. Settings switches keep the settings screen open, so changing one option does not send the player elsewhere.

Show directions selects an active quest and enables its arrow without switching an already enabled arrow off. Reading screens never accepts or completes quests, bypasses prerequisites or pays rewards; players still speak to the relevant NPC.

On supported Java clients the home and quest screens use native dialogues. Older or unsupported clients use a locked menu with the same navigation buttons; no book is required. Explicit `/quests book`, `/quests menu` and `/quests chat` remain available. Saved book/menu/chat preferences are retained for fallback NPC conversations; they no longer replace the `/quests` home screen. `/quests settings` opens the simpler settings screen.

Stop the server, replace the JAR and retain the CQuests data folder. No player progress or configuration reset is needed. Existing mail, animation fixes and optimisations are included.
