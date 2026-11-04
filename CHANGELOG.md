# CQuests changelog

Full notes for each release are in the RELEASE-x.y.z.md files and on the GitHub releases page.

CQuests **1.11.0**: every world boss is a jointed block model with 3+ attack animations, its own entrance and its own death, checked on 1.21.4, 26.2 and 26.3. See [RELEASE-1.11.0.md](RELEASE-1.11.0.md).

CQuests **1.10.1**: world boss animations, halos, a lighter fight loop and `/cq worldboss selftest`, checked on 1.21.4, 26.2 and 26.3. See [RELEASE-1.10.1.md](RELEASE-1.10.1.md).

CQuests **1.10.0**: weekly world bosses (20 + 4 seasonal) with a border stick, seasons, a tutorial quest and invite rewards. See [RELEASE-1.10.0.md](RELEASE-1.10.0.md).

CQuests **1.9.1**: `/cq test bossnext` to see every boss in turn and `/cq test companion` for Pip. See [RELEASE-1.9.1.md](RELEASE-1.9.1.md).

CQuests **1.9.0**: chapter costs from 5M that read your own balance placeholder, co-op dailies, Pip in boss fights, recipe tips from the server itself, daily money rolls and an elytra for chapter 5. See [RELEASE-1.9.0.md](RELEASE-1.9.0.md).

CQuests **1.8.1** raises chapter costs to 25k (chapter 2) up to 2.5M (chapter 10). See [RELEASE-1.8.1.md](RELEASE-1.8.1.md).

CQuests **1.8.0** gives chapters 6 to 10 twenty villagers each with mini bosses, makes chapters cost money, adds `/cq test boss` and friends, and points every compass at the next villager (`/quests where`). See [RELEASE-1.8.0.md](RELEASE-1.8.0.md).

CQuests **1.7.2** fixes the wheat farm: inside a saved field only the farm hoe harvests, new players get the free hoe automatically, and the action bar explains what to do. See [RELEASE-1.7.2.md](RELEASE-1.7.2.md).

CQuests **1.7.1** gives the Discord posts a proper embed: player face and skin, title, fields, a story progress bar and a footer. See [RELEASE-1.7.1.md](RELEASE-1.7.1.md).

CQuests **1.7.0** adds chapters 6 to 10 (50 new villagers, each chapter ending in a private boss fight), switched off until you run `/cq chapter 6 on`. It also adds Discord webhook announcements, daily quest streaks, `/cq scatterworld` across the whole world, a PlaceholderAPI placeholder for every number and name, and removes wheat from every quest. See [RELEASE-1.7.0.md](RELEASE-1.7.0.md).

CQuests **1.6.6** is a stability and performance release: NPCs under roofs or trees spawn again, a server-wide mob movement listener is gone, offline players leave memory, and renaming an NPC now changes its name everywhere (quest text, tracker, directions, mail, menus) and works from the console. See [RELEASE-1.6.6.md](RELEASE-1.6.6.md).

CQuests **1.3.3** separates and lifts NPC nameplates above private speech, improves name/level contrast and adds slower typing with a reading pause for every sentence. See [validation](AUDIT-1.3.3.md) and [farm testing](FARM-TESTING.md).

CQuests **1.3.2** adds `/cq merchant test [id|stop]`: a private temporary walk and trade preview that does not spend items or money or alter saved merchants. See [setup](MERCHANTS-1.3.md) and [validation](AUDIT-1.3.2.md).

CQuests **1.3.1** simplifies merchant setup to spawn, wand trail, then end (including final facing), adds an OP skin command for quest NPCs, and bounds queued GUI callbacks during packet bursts. See [merchant setup](MERCHANTS-1.3.md) and [validation](AUDIT-1.3.1.md).


Version 1.3 adds five travelling merchant presets, operator-only route and trade editing, item/money/mixed trades, and additive story twists. See [MERCHANTS-1.3.md](MERCHANTS-1.3.md) for placement, GUI controls and security boundaries.

Version 1.2.3 closes an offhand farm-container bypass, preserves placed-block quest protection through piston movement, and prevents conversation chat loss during buffer overflow or conversation completion. It includes the previous reconnect/save, personal-tool and client compatibility fixes. See [AUDIT-1.2.3.md](AUDIT-1.2.3.md) and [AUDIT-1.2.2.md](AUDIT-1.2.2.md) for validation and remaining limits.

Version 1.2 adds private letter-by-letter NPC speech, native Minecraft dialog choices on capable servers, a paginated book journal, custom levels, personal wheat tools, anvil upgrades and exact WorldGuard-bound polygon farms. One click harvests one mature wheat and fully regrows it after one second. Tool unlocks return to a personal locker outside the farm. Chapter broadcasts and new farming/level achievements reward progress. The boss bar, direction arrow/meters and mandatory side-job quotas remain off by default. See [INSTALL-1.2.md](INSTALL-1.2.md) for setup, preservation, pacing and rollback.
