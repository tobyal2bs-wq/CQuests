# Story generator

`story.py` holds the 100 story villagers (name, lines, quest, objectives) as one table, and
`emit.py` turns it into `src/main/resources/npcs.yml` and `quests.yml`:

    python3 tools/story/emit.py tools/story src/main/resources

You can also edit the YAML files directly; the plugin only reads the YAML. Use the script when
you want to add or reorder villagers in bulk (chapters, levels and rewards are worked out from the row order).

The eight optional 1.1 side villagers live in side-villagers.yml and are appended by emit.py.
They do not change story order, quest IDs or the side-quest seed. Their chapter field controls
when they unlock and which chapter selector scatters them.
