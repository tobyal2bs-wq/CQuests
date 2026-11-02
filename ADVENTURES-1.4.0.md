# NPC memories, companions and chapter progression

## Who belongs at spawn

The default residents are **Stephan, Jerry, Rosie, Copper Jack, Luma and B.O.B**, with **Granny Marigold** providing daily jobs. B.O.B can be seen before his story chapter opens, but his quests still require the earlier story steps. The other spawn residents also keep their existing story roles. The default spawn list is `spawning.camp-npcs`; B.O.B and daily NPCs stay out of world scattering.

Run `/cq camp` to deliberately arrange these residents around the spawn of the world you are currently in. Existing saved positions are retained until you choose to move them. `/cq npc place B.O.B` places B.O.B on safe ground where you are standing. `/cq scatterworld chapter2 10000 10000` scatters eligible Chapter 2 NPCs in your current world; the optional world argument still allows an explicit target. Spawn residents are skipped, and player progress is retained.

## Levels and daily work

Daily work begins at **Wayfarer level 10**, including the daily NPC's displayed level and the daily quest requirements. Its jobs are generated for that entry level. Existing daily cooldowns remain in place.

The default story chapter entry levels are **0, 100, 200, 300 and 400** for Chapters 1 through 5. Each quest also retains its individual requirement if that is higher. Levels unlock eligibility; they never complete or bypass previous quest requirements. Change the gates under `progression.chapter-levels` in `config.yml` and the daily entry level under `progression.daily-min-level`.

The former shipped 100-level cap upgrades to **500**. `farming.yml.before-1.4.0` preserves the previous file. Custom caps other than 100 are retained; supported maximums extend to 1000. Saved XP, unlocked tools and completed/active quest records are retained. Expanding the curve changes the level that existing XP corresponds to; it does not remove earned XP. Keep the maximum high enough for your chapter gates. Wheat still earns custom skill XP and does not consume vanilla experience.

## What NPCs remember

NPCs recognise returning players by UUID and remember completed work. Three authored decisions currently appear when you speak to the quest giver after finishing their story quest:

- **Martha:** promise to stand with the fields, or refuse future help. Her brother **Steve** reacts to your answer.
- **Lucy:** promise to protect the couriers' identities, or withhold that promise. Her cousin **Ned** reacts too.
- **Esme:** commit to bringing the King home, or leave his fate to others.

The NPC types the question over their head, then another click opens the two-choice menu. Leaving the menu postpones your answer. A selected answer is saved once for that journey; replaying clicks cannot change it. Returning NPCs give warm or wary reactions. These choices affect dialogue, not payouts, quest order or an unannounced punishment system. Ordinary mining, farming and chat are not judged or recorded. Definitions and named relatives live in `memories.yml`; set `enabled: false` there to disable these authored choices. An explicit administrator journey reset also clears that journey's decisions.

## Pip and the vessel

**Pip** joins during **Scarecrow Watch** (`story_martha`) and **Eve of Waking** (`story_iona`). He walks behind his owner, has a private two-line nameplate, and adds a small hit to a nearby matching quest monster after the player attacks it. He does not fight players, passive animals, pets or unrelated monsters. Original hit cancellation is respected, and nearby assistance has its own cooldown. Finishing the objectives, dying, leaving the world, logout or cleanup removes him. A blocked or distant route withdraws the companion rather than teleporting him through terrain. At most 32 companions can be active.

During **The King Wakes** (`story_aldis`), speak to **Aldis** and click **Face the vessel** when ready. `/quests encounter` is an alternative while that unfinished quest is active. Use Survival or Adventure in a non-Peaceful world with clear, solid ground beside you.

The quest Wither is bound to its player. Its three heads target that player; other players cannot damage it, and its damage/projectiles are blocked against bystanders. Its terrain destruction and ordinary drops/XP are suppressed; the existing quest reward is unchanged. Only one encounter per player and four server-wide can run. Leaving the 48-block encounter area, death, logout, a ten-minute timeout or cleanup withdraws it without kill credit. A defeated vessel credits one owner objective, and a finished objective cannot summon another vessel. Ordinary naturally spawned Withers retain their normal behavior.

The `adventures.enabled`, `adventures.companions` and `adventures.wither` toggles are in `config.yml`.

## Speech layout and installation

All quest nameplates use the same name/level layout, with chapter colours and a distinct daily colour. The plate sits close above the speech and moves only as needed for its line count. The extra “Choose your next step” line is removed; “Click to continue” types progressively too. Sentence reading pauses and click-to-finish controls remain.

Stop the server, back up the CQuests data folder, replace the JAR and keep the data folder. Do not reset player files. Test the actual custom Vault economy and appearance in your Minecraft client on staging; automated protocol checks do not establish every plugin combination or visual preference.
