# CQuests 1.6.3

Targeted reductions in repeated work, preserving gameplay and saved player data:

- The shared display loop reuses the farm membership result for directions instead of querying the same boundary again. Harvests and command/tool restrictions retain their independent checks.
- Farm regrowth saves skip YAML serialisation and disk replacement when the pending crop set matches the last successful save. Changed crops, retries after a failed save and the shutdown drain still persist normally.
- Rereading letters and navigating an already delivered inbox no longer queue redundant player snapshots. New deliveries, first reads and new replies still save immediately.
- Overhead speech builds plain text components directly per letter, avoiding a MiniMessage parse for every character. Authored chat formatting is retained.
- After the continue prompt finishes typing, idle conversation checks run every ten ticks instead of every tick. Clicks still go directly through the interaction handler; speech animation remains tick based. Leaving the conversation radius or reaching its timeout is detected within half a second while idle.

These changes reduce specific work counts. They are not a measured live-server TPS improvement or a guarantee of zero lag. Results on the hosted server depend on player count, entities, loaded chunks, hardware and other plugins. No quest requirements, rewards, harvest cooldowns, security checks or AI defaults were changed.

Stop the server, replace the JAR and keep the CQuests data folder. No configuration reset or progress migration is required.
