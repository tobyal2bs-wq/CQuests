# Generates src/main/resources/worldbosses.yml (python3 tools/worldboss/gen_bosses.py)
B = []
def boss(id, name, title, entity, health, scale, damage, bar, particle, color, abilities, minion=None, minions=3,
         equipment=None, mount=None, rider=None, speed=0, armor=0, season="", money=50000, top=150000, items=None, top_items=None, size=1, secs=8, halo=None):
    B.append(dict(id=id, name=name, title=title, entity=entity, health=health, scale=scale, damage=damage, bar=bar,
                  particle=particle, color=color, abilities=abilities, minion=minion, minions=minions, equipment=equipment or {},
                  mount=mount, rider=rider, speed=speed, armor=armor, season=season, money=money, top=top,
                  items=items or [], top_items=top_items or [], size=size, secs=secs, halo=halo))

boss("gravelord", "<gradient:#6a1b9a:#e040fb><bold>The Gravelord</bold></gradient>", "Lord of the Restless Dead", "WITHER_SKELETON",
     1600, 2.2, 13, "PURPLE", "SOUL_FIRE_FLAME", "#7b1fa2", ["minions", "darkness", "shockwave", "blink"], "SKELETON", 4,
     {"head": "NETHERITE_HELMET", "chest": "NETHERITE_CHESTPLATE", "hand": "NETHERITE_SWORD"}, armor=10,
     items=["NETHERITE_SCRAP 1", "GOLDEN_APPLE 4"], top_items=["ENCHANTED_GOLDEN_APPLE 1"])
boss("molten_colossus", "<gradient:#ff6f00:#ffd54f><bold>The Molten Colossus</bold></gradient>", "Heart of the Forge", "IRON_GOLEM",
     2200, 2.4, 16, "RED", "LAVA", "#ff6f00", ["fire_ring", "quake", "leap", "shockwave"], armor=12,
     items=["IRON_BLOCK 4", "GOLDEN_APPLE 3"], top_items=["NETHERITE_INGOT 1"])
boss("broodmother", "<gradient:#33691e:#aed581><bold>The Broodmother</bold></gradient>", "Queen of the Deep Webs", "SPIDER",
     1400, 3.0, 10, "GREEN", "SPORE_BLOSSOM_AIR", "#558b2f", ["poison", "minions", "leap", "pull"], "CAVE_SPIDER", 5, speed=0.34,
     items=["STRING 32", "GOLDEN_APPLE 3"], top_items=["DIAMOND 6"])
boss("frost_jarl", "<gradient:#4fc3f7:#e1f5fe><bold>Jarl Hrimfrost</bold></gradient>", "The Winter That Walks", "STRAY",
     1500, 2.1, 11, "BLUE", "SNOWFLAKE", "#81d4fa", ["frost", "volley", "minions", "shockwave"], "STRAY", 4,
     {"head": "DIAMOND_HELMET", "chest": "LEATHER_CHESTPLATE", "hand": "BOW"}, armor=8,
     items=["BLUE_ICE 16", "GOLDEN_APPLE 3"], top_items=["DIAMOND 8"])
boss("warlord_gruk", "<gradient:#ffb300:#fff176><bold>Warlord Gruk</bold></gradient>", "Gold-Hungry Tyrant of the Bastion", "PIGLIN_BRUTE",
     1700, 2.0, 15, "YELLOW", "WAX_ON", "#ffc107", ["leap", "shockwave", "minions", "roar"], "PIGLIN_BRUTE", 3,
     {"head": "GOLDEN_HELMET", "chest": "GOLDEN_CHESTPLATE", "legs": "GOLDEN_LEGGINGS", "hand": "GOLDEN_AXE"}, armor=10,
     items=["GOLD_BLOCK 4", "GOLDEN_CARROT 16"], top_items=["GOLD_BLOCK 16"])
boss("tide_tyrant", "<gradient:#00838f:#80deea><bold>The Tide Tyrant</bold></gradient>", "Drowned King of the Sunken Fleet", "DROWNED",
     1500, 2.2, 12, "BLUE", "NAUTILUS", "#00acc1", ["pull", "volley", "frost", "minions"], "DROWNED", 4,
     {"head": "TURTLE_HELMET", "hand": "TRIDENT"}, armor=8,
     items=["PRISMARINE_SHARD 16", "GOLDEN_APPLE 3"], top_items=["HEART_OF_THE_SEA 1"])
boss("storm_herald", "<gradient:#3949ab:#b3e5fc><bold>The Storm Herald</bold></gradient>", "Voice of the Thunderhead", "EVOKER",
     1200, 2.0, 10, "BLUE", "ELECTRIC_SPARK", "#5c6bc0", ["lightning", "levitate", "blink", "pull"], armor=6, secs=7,
     items=["LAPIS_BLOCK 4", "GOLDEN_APPLE 3"], top_items=["TOTEM_OF_UNDYING 1"])
boss("ironhide_behemoth", "<gradient:#5d4037:#bcaaa4><bold>The Ironhide Behemoth</bold></gradient>", "War Beast of the Raid", "RAVAGER",
     2400, 1.7, 15, "RED", "CAMPFIRE_COSY_SMOKE", "#6d4c41", ["leap", "shockwave", "roar", "quake"], rider="PILLAGER", armor=12,
     items=["EMERALD 24", "GOLDEN_APPLE 3"], top_items=["EMERALD_BLOCK 6"])
boss("bloodtusk", "<gradient:#b71c1c:#ff8a80><bold>Bloodtusk</bold></gradient>", "The Crimson Charger", "HOGLIN",
     1800, 2.0, 14, "RED", "CRIMSON_SPORE", "#c62828", ["leap", "shockwave", "minions", "roar"], "HOGLIN", 2, speed=0.36, armor=8,
     items=["COOKED_PORKCHOP 32", "GOLDEN_APPLE 3"], top_items=["NETHERITE_SCRAP 2"])
boss("cinder_sovereign", "<gradient:#ff3d00:#ffea00><bold>The Cinder Sovereign</bold></gradient>", "Crowned in Living Flame", "BLAZE",
     1300, 2.3, 10, "YELLOW", "FLAME", "#ff9100", ["fire_ring", "minions", "blink", "levitate"], "BLAZE", 3, armor=6,
     items=["BLAZE_ROD 12", "GOLDEN_APPLE 3"], top_items=["NETHER_STAR 1"])
boss("volatile_colossus", "<gradient:#00e676:#ccff90><bold>The Volatile Colossus</bold></gradient>", "It Hisses. It Never Stops.", "CREEPER",
     1400, 2.6, 0, "GREEN", "HAPPY_VILLAGER", "#00e676", ["detonate", "detonate", "leap", "pull"], speed=0.3, armor=6, secs=6,
     items=["TNT 8", "GOLDEN_APPLE 3"], top_items=["MUSIC_DISC_PIGSTEP 1"])
boss("king_gloop", "<gradient:#7cb342:#dce775><bold>King Gloop</bold></gradient>", "Monarch of the Swamp", "SLIME",
     1600, 1, 12, "GREEN", "ITEM_SLIME", "#9ccc65", ["leap", "quake", "minions", "poison"], "SLIME", 4, size=10, armor=6,
     items=["SLIME_BLOCK 8", "GOLDEN_APPLE 3"], top_items=["DIAMOND 8"])
boss("executioner", "<gradient:#263238:#90a4ae><bold>The Executioner</bold></gradient>", "Axe of the Woodland Mansion", "VINDICATOR",
     1500, 1.9, 17, "WHITE", "SMOKE", "#455a64", ["leap", "shockwave", "minions", "roar"], "VINDICATOR", 3,
     {"head": "NETHERITE_HELMET", "hand": "NETHERITE_AXE"}, armor=10,
     items=["EMERALD 24", "GOLDEN_APPLE 3"], top_items=["TOTEM_OF_UNDYING 1"])
boss("pharaoh", "<gradient:#f9a825:#fff59d><bold>Pharaoh Ankhamun</bold></gradient>", "Risen from the Buried Temple", "HUSK",
     1600, 2.2, 12, "YELLOW", "WAX_OFF", "#fbc02d", ["darkness", "poison", "minions", "blink"], "HUSK", 4,
     {"head": "GOLDEN_HELMET", "chest": "GOLDEN_CHESTPLATE", "hand": "GOLDEN_SWORD"}, armor=8,
     items=["GOLD_INGOT 16", "GOLDEN_APPLE 3"], top_items=["ENCHANTED_GOLDEN_APPLE 1"])
boss("ruinmaw", "<gradient:#ad1457:#f48fb1><bold>Ruinmaw</bold></gradient>", "The Rotting Juggernaut", "ZOGLIN",
     2000, 2.2, 15, "PINK", "DAMAGE_INDICATOR", "#d81b60", ["leap", "quake", "shockwave", "roar"], speed=0.35, armor=10,
     items=["LEATHER 24", "GOLDEN_APPLE 3"], top_items=["NETHERITE_SCRAP 2"])
boss("hexmother", "<gradient:#6a1b9a:#ce93d8><bold>Hexmother Morwen</bold></gradient>", "Brewer of a Thousand Curses", "WITCH",
     1200, 1.9, 8, "PURPLE", "WITCH", "#8e24aa", ["levitate", "poison", "blink", "heal", "darkness"], armor=4, secs=7,
     items=["BREWING_STAND 1", "GLOWSTONE_DUST 32", "GOLDEN_APPLE 3"], top_items=["ENCHANTED_GOLDEN_APPLE 1"])
boss("void_walker", "<gradient:#311b92:#b388ff><bold>The Void Walker</bold></gradient>", "It Was Never Really Here", "ENDERMAN",
     1400, 1.6, 13, "PURPLE", "REVERSE_PORTAL", "#651fff", ["blink", "darkness", "levitate", "pull"], armor=6, secs=6,
     items=["ENDER_PEARL 16", "GOLDEN_APPLE 3"], top_items=["SHULKER_SHELL 4"])
boss("fenrir", "<gradient:#424242:#e0e0e0><bold>Fenrir</bold></gradient>", "The Wolf That Swallows the Moon", "WOLF",
     1500, 3.0, 13, "WHITE", "WHITE_ASH", "#9e9e9e", ["leap", "frost", "minions", "roar"], "WOLF", 4, speed=0.42, armor=8,
     items=["BONE 32", "GOLDEN_APPLE 3"], top_items=["DIAMOND 8"])
boss("tempest", "<gradient:#80deea:#ffffff><bold>Tempest</bold></gradient>", "The Storm Given Form", "BREEZE",
     1200, 2.5, 10, "WHITE", "GUST", "#b2ebf2", ["levitate", "pull", "shockwave", "lightning"], "BREEZE", 2, armor=6, secs=7,
     items=["BREEZE_ROD 8", "GOLDEN_APPLE 3"], top_items=["HEAVY_CORE 1"])
boss("pale_watcher", "<gradient:#757575:#ff6d00><bold>The Pale Watcher</bold></gradient>", "Don't Look Away", "CREAKING",
     1500, 2.0, 14, "WHITE", "WHITE_ASH", "#ff6d00", ["darkness", "blink", "quake", "roar"], armor=10,
     items=["PALE_OAK_LOG 32", "GOLDEN_APPLE 3"], top_items=["RESIN_BLOCK 8"])
# Seasonal (only scheduled while their season is on)
boss("headless_horseman", "<gradient:#e65100:#ffab40><bold>The Headless Horseman</bold></gradient>", "Rider of All Hallows' Eve", "SKELETON",
     1600, 1.8, 12, "RED", "FLAME", "#ff6d00", ["volley", "fire_ring", "darkness", "minions"], "SKELETON", 3,
     {"head": "JACK_O_LANTERN", "chest": "LEATHER_CHESTPLATE", "legs": "LEATHER_LEGGINGS", "hand": "BOW"}, mount="SKELETON_HORSE", armor=8,
     season="halloween", money=60000, top=200000, items=["PUMPKIN_PIE 16", "JACK_O_LANTERN 4"], top_items=["ENCHANTED_GOLDEN_APPLE 1"])
boss("old_man_winter", "<gradient:#b3e5fc:#ffffff><bold>Old Man Winter</bold></gradient>", "The Blizzard Returns", "STRAY",
     1700, 2.6, 12, "BLUE", "SNOWFLAKE", "#e1f5fe", ["frost", "volley", "shockwave", "minions"], "STRAY", 4,
     {"head": "LEATHER_HELMET", "chest": "LEATHER_CHESTPLATE", "hand": "BOW"}, armor=8,
     season="winter", money=60000, top=200000, items=["SNOW_BLOCK 16", "COOKIE 16"], top_items=["DIAMOND 12"])
boss("killer_bunny", "<gradient:#ffffff:#ff1744><bold>The Killer Bunny</bold></gradient>", "Small, Fluffy, Merciless", "RABBIT",
     900, 3.5, 12, "PINK", "CHERRY_LEAVES", "#ff80ab", ["leap", "leap", "minions", "shockwave"], "RABBIT", 4, speed=0.5, armor=4,
     season="spring", money=60000, top=200000, items=["RABBIT_STEW 4", "GOLDEN_CARROT 16"], top_items=["RABBIT_FOOT 4"])
boss("sunscorch", "<gradient:#ff6d00:#ffea00><bold>Sunscorch</bold></gradient>", "Melting On Holiday", "MAGMA_CUBE",
     1500, 1, 12, "YELLOW", "LAVA", "#ffab00", ["fire_ring", "leap", "quake", "volley"], "MAGMA_CUBE", 3, size=10, armor=8,
     season="summer", money=60000, top=200000, items=["MAGMA_BLOCK 16", "MELON_SLICE 32"], top_items=["NETHERITE_SCRAP 2"])
boss("great_gourd", "<gradient:#ff9100:#7c4dff><bold>The Great Gourd</bold></gradient>", "Trick or Treat, Mostly Trick", "ZOMBIE",
     1500, 2.0, 12, "YELLOW", "WITCH", "#ff9100", ["fire_ring", "minions", "poison", "leap"], "ZOMBIE", 4, armor=8,
     season="halloween", money=60000, top=200000, items=["PUMPKIN_PIE 16", "COOKIE 32"], top_items=["DIAMOND 8"])
boss("frostbottom", "<gradient:#e1f5fe:#ff7043><bold>Frostbottom</bold></gradient>", "The Snowman With a Grudge", "STRAY",
     1600, 2.0, 12, "WHITE", "SNOWFLAKE", "#b3e5fc", ["frost", "volley", "quake", "minions"], "STRAY", 4, armor=8,
     season="winter", money=60000, top=200000, items=["SNOW_BLOCK 16", "CARROT 32"], top_items=["DIAMOND 8"])
boss("clucksworth", "<gradient:#ffffff:#ff5252><bold>Clucksworth</bold></gradient>", "The Chicken That Came First", "ZOMBIE",
     1400, 2.0, 12, "WHITE", "CLOUD", "#ffeb3b", ["leap", "minions", "shockwave", "volley"], "ZOMBIE", 4, speed=0.3, armor=6,
     season="spring", money=60000, top=200000, items=["EGG 16", "COOKED_CHICKEN 16"], top_items=["DIAMOND 8"])
boss("admiral_pinchworth", "<gradient:#ff5252:#ffd180><bold>Admiral Pinchworth</bold></gradient>", "Lord of the Sandcastle", "SPIDER",
     1500, 2.0, 12, "RED", "SPLASH", "#ff5252", ["leap", "minions", "pull", "volley"], "SILVERFISH", 5, speed=0.32, armor=10,
     season="summer", money=60000, top=200000, items=["SAND 32", "TROPICAL_FISH 8"], top_items=["HEART_OF_THE_SEA 1"])

def q(s): return '"' + s.replace('"', '\\"') + '"'
out = ["# CQuests world bosses. One wakes each week at the arena you set with /cq worldboss setspawn <arena>.",
       "# Draw the border it can never leave with /cq worldboss wand <arena> (left-click blocks for corners).",
       "# World bosses only attack players, never break, burn or change blocks, drop nothing and are never saved",
       "# into the world. Everyone who did at least world-bosses.min-damage-percent of its health gets rewards;",
       "# the top 3 by damage get top-money (split 1/1, 1/2, 1/3) and top-items, and the best gets top-commands.",
       "# abilities: lightning, shockwave, minions, fire_ring, pull, leap, poison, blink, frost, volley, darkness,",
       "#            levitate, heal, quake, detonate, roar",
       "# particle: any Bukkit particle name without extra data (FLAME, SNOWFLAKE, PORTAL, ...). bar: boss bar colour.",
       "# season: halloween, winter, spring or summer. Seasonal bosses take the weekly slot while that season is on.",
       "# Each boss is drawn with block displays from worldboss-models.json (its own shape, three attack animations,",
       "# its own entrance and death). The real mob is invisible and only gives the AI and hitbox, so 'scale' and",
       "# 'equipment' only matter with 'model: none' or world-bosses.models: false in config.yml.",
       "# Try any of them with /cq test worldboss <id>, or all of them with /cq worldboss selftest.",
       "bosses:"]
for b in B:
    out.append(f"  {b['id']}:")
    out.append(f"    name: {q(b['name'])}")
    out.append(f"    title: {q(b['title'])}")
    out.append(f"    entity: {b['entity']}")
    if b['mount']: out.append(f"    mount: {b['mount']}")
    if b['rider']: out.append(f"    rider: {b['rider']}")
    if b['size'] > 1: out.append(f"    size: {b['size']}")
    out.append(f"    health: {b['health']}")
    out.append(f"    scale: {b['scale']}")
    out.append(f"    damage: {b['damage']}")
    if b['speed']: out.append(f"    speed: {b['speed']}")
    if b['armor']: out.append(f"    armor: {b['armor']}")
    out.append(f"    bar: {b['bar']}")
    out.append(f"    glow: true")
    out.append(f"    particle: {b['particle']}")
    out.append(f"    color: {q(b['color'])}")
    if b['equipment']:
        out.append("    equipment:")
        for k, v in b['equipment'].items(): out.append(f"      {k}: {v}")
    if b['minion']:
        out.append(f"    minion: {b['minion']}")
        out.append(f"    minions: {b['minions']}")
    out.append(f"    ability-seconds: {b['secs']}")
    out.append("    abilities: [" + ", ".join(b['abilities']) + "]")
    if b['season']: out.append(f"    season: {b['season']}")
    out.append("    rewards:")
    out.append(f"      money: {b['money']}")
    out.append(f"      top-money: {b['top']}")
    out.append("      items: [" + ", ".join(q(i) for i in b['items']) + "]")
    out.append("      top-items: [" + ", ".join(q(i) for i in b['top_items']) + "]")
    out.append("      commands: []")
    out.append("      top-commands: []")
open(__import__('os').path.join(__import__('os').path.dirname(__file__), '../../src/main/resources/worldbosses.yml'), 'w').write("\n".join(out) + "\n")
print(len(B))
