# Story generator

`story.py` holds the 100 story villagers (name, lines, quest, objectives) as one table, and
`emit.py` turns it into `src/main/resources/npcs.yml` and `quests.yml`:

    python3 tools/story/emit.py tools/story src/main/resources

You can also edit the YAML files directly; the plugin only reads the YAML. Use the script when
you want to add or reorder villagers in bulk (chapters, levels and rewards are worked out from the row order).
