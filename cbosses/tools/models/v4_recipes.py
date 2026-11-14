"""Openings and deaths for the v3 and v4 bosses, in the same language as v2_recipes: each boss arrives and
dies its own way, built from its own pieces. Ticks, blocks and vh as in v2_recipes."""
from v2_recipes import S, fx, gone

SPAWN, DEATH = {}, {}

# ------------------------------------------------------------------------------------------------ mythic

SPAWN["the_listener"] = [S("move", 0, vh=[0, -1.05, 0]), fx(0, "SCULK_CHARGE_POP", 90, "ENTITY_WARDEN_EMERGE", 0.7, y=0, spread=3, ring=5),
    S("move", 6, 80, vh=[0, 1.05, 0]), fx(30, "BLOCK", 140, "ENTITY_WARDEN_DIG", 0.6, y=0, spread=3, block="SCULK"),
    S("light", 86, on=True, only="heart"), fx(88, "SCULK_SOUL", 60, "ENTITY_WARDEN_HEARTBEAT", 0.8, y=0.5),
    S("shake", 92, 12, only="tendril"), fx(96, sound="ENTITY_WARDEN_TENDRIL_CLICKS", pitch=0.6),
    S("anim", 104, 30, name="roar"), fx(110, "SONIC_BOOM", 1, "ENTITY_WARDEN_ROAR", 0.7, y=0.8)]
DEATH["the_listener"] = [S("flash", 0, 4, block="cyan_concrete"), fx(0, sound="ENTITY_WARDEN_DEATH", pitch=0.5), S("anim", 0, 30, name="die_kneel"),
    fx(12, sound="ENTITY_WARDEN_HEARTBEAT", pitch=0.7), fx(28, sound="ENTITY_WARDEN_HEARTBEAT", pitch=0.5),
    S("move", 34, 24, v=[0, 3, 0], only="heart"), S("spin", 34, 24, deg=360, only="heart"), fx(56, "SONIC_BOOM", 1, "ENTITY_WARDEN_SONIC_BOOM", 0.5, y=0.6),
    S("shatter", 58, pieces=4, power=3, up=2, only="heart"), S("swap", 60, block="sculk", order="up", stagger=24),
    S("scale", 84, 30, s=[1.5, 0.04, 1.5], only="!heart"), fx(86, "SCULK_CHARGE_POP", 140, "BLOCK_SCULK_SPREAD", 0.6, y=0, spread=4), gone(114, 10)]

SPAWN["withered_tyrant"] = [S("shrink", 0, s=0), fx(0, "SMOKE", 80, "ENTITY_WITHER_SPAWN", 0.7, y=0.5, spread=2),
    S("pose", 4, 20, only="ring3"), S("pose", 20, 30, order="up", stagger=24, only="core"), fx(30, "SOUL_FIRE_FLAME", 60, "BLOCK_SOUL_SAND_BREAK", 0.6, y=0.4),
    S("pose", 48, 10, only="armL"), S("pose", 54, 10, only="armR"), S("pose", 62, 14, only="head"), S("light", 74, on=True, only="lit"),
    S("pose", 76, 20, only="ring2"), fx(78, "EXPLOSION", 3, "ENTITY_WITHER_SPAWN", 1.0, y=0.6), S("anim", 82, 22, name="pulse")]
DEATH["withered_tyrant"] = [S("flash", 0, 4, block="light_blue_concrete"), fx(0, "SOUL_FIRE_FLAME", 80, "ENTITY_WITHER_DEATH", 0.6),
    S("burst", 4, 10, power=4, up=3, tilt=360, only="ring2"), S("anim", 0, 26, name="die_drop"),
    S("fling", 20, power=3, up=5, tilt=240, only="armL"), S("fling", 24, power=3, up=5, tilt=240, only="armR"),
    S("spin", 28, 30, deg=540, only="head"), S("move", 28, 30, v=[0, 5, 0], only="head"), fx(56, "EXPLOSION_EMITTER", 1, "ENTITY_GENERIC_EXPLODE", 0.6, y=1),
    S("shatter", 58, pieces=4, power=3, up=2, only="head"), S("drop", 40, 14, tilt=60, rand=2, only="core"), S("drop", 40, 14, tilt=60, rand=2, only="ring3"),
    fx(60, "LARGE_SMOKE", 80, "BLOCK_SOUL_SAND_BREAK", 0.5, y=0.2, spread=3), gone(84, 12)]

SPAWN["ender_wyrm"] = [S("move", 0, v=[0, 24, -30]), S("anim", 0, 40, name="walk"), fx(0, "PORTAL", 120, "ENTITY_ENDER_DRAGON_GROWL", 0.6, y=0.8, spread=4),
    S("move", 4, 50, v=[0, -24, 30]), fx(40, "DRAGON_BREATH", 80, "ENTITY_ENDER_DRAGON_FLAP", 0.6, y=0.3, spread=4),
    fx(54, "EXPLOSION", 3, "ENTITY_GENERIC_EXPLODE", 0.6, y=0, spread=3), S("anim", 56, 30, name="howl"), fx(62, "DRAGON_BREATH", 120, "ENTITY_ENDER_DRAGON_AMBIENT", 0.6, y=0.9, spread=2)]
DEATH["ender_wyrm"] = [S("flash", 0, 4, block="magenta_concrete"), fx(0, sound="ENTITY_ENDER_DRAGON_DEATH", pitch=0.7), S("anim", 0, 30, name="die_side"),
    S("light", 6, on=True, only="unlit"), fx(10, "END_ROD", 160, "BLOCK_BEACON_POWER_SELECT", 0.5, y=0.5, spread=3),
    S("shake", 10, 40), S("swap", 40, block="end_rod", order="up", stagger=30), fx(50, "FLASH", 1, "ENTITY_GENERIC_EXPLODE", 0.5, y=0.6),
    S("burst", 70, 14, power=3, up=6, tilt=360, rand=2), fx(72, "DRAGON_BREATH", 160, "ENTITY_ENDER_DRAGON_FLAP", 0.4, y=0.4, spread=4), gone(90, 12)]

# ------------------------------------------------------------------------------------------------ normal

SPAWN["old_ironroot"] = [S("move", 0, vh=[0, -1.0, 0]), fx(0, "BLOCK", 80, "BLOCK_ROOTED_DIRT_BREAK", 0.6, y=0, spread=3, block="ROOTED_DIRT"),
    S("move", 4, 50, vh=[0, 1.0, 0]), S("shake", 30, 20), fx(50, "HAPPY_VILLAGER", 40, "ENTITY_IRON_GOLEM_REPAIR", 0.6, y=0.9, spread=2),
    S("anim", 56, 26, name="slam"), fx(70, "BLOCK", 100, "ENTITY_IRON_GOLEM_ATTACK", 0.6, y=0, spread=3, block="MOSS_BLOCK")]
DEATH["old_ironroot"] = [S("flash", 0, 3), fx(0, sound="ENTITY_IRON_GOLEM_DEATH", pitch=0.6), S("anim", 0, 30, name="die_kneel"),
    S("swap", 20, block="moss_block", order="up", stagger=40), fx(30, "SPORE_BLOSSOM_AIR", 80, "BLOCK_AZALEA_LEAVES_BREAK", 0.7, y=0.7, spread=2),
    S("scale", 64, 20, s=[1.2, 0.5, 1.2]), fx(70, "HAPPY_VILLAGER", 40, "BLOCK_MOSS_PLACE", 0.6, y=0.3, spread=3), gone(86, 14)]

SPAWN["grave_marshal"] = [S("shrink", 0, s=0), fx(0, "SOUL", 60, "ENTITY_SKELETON_AMBIENT", 0.5, y=0, spread=2),
    S("pose", 4, 4, order="up", stagger=40, only="!hammer"), fx(20, "BLOCK", 60, "BLOCK_BONE_BLOCK_BREAK", 0.6, y=0.4, block="BONE_BLOCK"),
    S("move", 44, vh=[0, 1.4, 0], only="hammer"), S("pose", 46, 10, only="hammer"), fx(56, "EXPLOSION", 1, "BLOCK_ANVIL_LAND", 0.6, y=0.6),
    S("anim", 58, 28, name="slam")]
DEATH["grave_marshal"] = [S("flash", 0, 3, block="purple_concrete"), fx(0, sound="ENTITY_SKELETON_DEATH", pitch=0.5), S("anim", 0, 28, name="die_front"),
    S("fling", 10, power=3, up=3, tilt=200, only="shield"), S("drop", 16, 10, tilt=90, only="hammer"),
    S("burst", 30, 12, power=1.5, up=4, tilt=180, rand=1.2, only="!shield"), fx(30, "BLOCK", 120, "BLOCK_BONE_BLOCK_BREAK", 0.5, y=0.4, spread=2, block="BONE_BLOCK"),
    S("drop", 44, 14, tilt=90, rand=2, only="!shield"), fx(60, "SOUL", 40, "PARTICLE_SOUL_ESCAPE", 0.6, y=0.8), gone(76, 12)]

SPAWN["mayor_grumble"] = [S("move", 0, v=[0, 12, 0]), S("shrink", 0, s=0, only="hat"), fx(0, "HAPPY_VILLAGER", 30, "ENTITY_VILLAGER_AMBIENT", 0.6, y=0),
    S("move", 2, 14, v=[0, -12, 0]), fx(16, "BLOCK", 60, "ENTITY_GENERIC_BIG_FALL", 0.6, y=0, spread=2, block="DIRT"), S("scale", 16, 6, s=[1.3, 0.7, 1.3]),
    S("pose", 22, 6), S("move", 30, vh=[0, 1.2, 0], only="hat"), S("pose", 32, 12, only="hat"), fx(44, sound="ENTITY_VILLAGER_NO", pitch=0.6),
    S("anim", 46, 24, name="roar")]
DEATH["mayor_grumble"] = [S("flash", 0, 3, block="emerald_block"), fx(0, sound="ENTITY_VILLAGER_DEATH", pitch=0.6), S("fling", 2, power=2, up=6, tilt=360, only="hat"),
    S("shake", 4, 16), S("anim", 10, 28, name="die_back"), fx(30, "HAPPY_VILLAGER", 60, "ENTITY_VILLAGER_HURT", 0.5, y=0.6),
    S("burst", 40, 10, power=2, up=3, tilt=180, rand=1, only="!hat"), fx(42, "ITEM", 40, "ENTITY_ITEM_PICKUP", 0.6, y=0.4, item="EMERALD"), gone(62, 10)]

SPAWN["siegebreaker"] = [S("move", 0, v=[0, 0, -14]), S("anim", 0, 40, name="walk"), fx(0, "CLOUD", 40, "EVENT_RAID_HORN", 0.8, y=0, spread=3),
    S("move", 2, 34, v=[0, 0, 14]), fx(20, "BLOCK", 80, "ENTITY_RAVAGER_STEP", 0.6, y=0, spread=2.5, block="DIRT"),
    S("anim", 40, 30, name="rear"), fx(56, "EXPLOSION", 2, "ENTITY_RAVAGER_ROAR", 0.7, y=0.6)]
DEATH["siegebreaker"] = [S("flash", 0, 3), fx(0, sound="ENTITY_RAVAGER_DEATH", pitch=0.6), S("anim", 0, 30, name="die_side"),
    S("fling", 12, power=3, up=6, tilt=120, only="banner"), fx(26, "BLOCK", 120, "ENTITY_GENERIC_BIG_FALL", 0.5, y=0, spread=3, block="DIRT"),
    S("swap", 40, block="cobblestone", order="random", stagger=20), S("shatter", 60, pieces=3, power=2, up=2, order="up", stagger=16), gone(80, 12)]

SPAWN["old_tusker"] = [S("move", 0, vh=[0, -1.0, 0]), fx(0, "CRIMSON_SPORE", 100, "BLOCK_NYLIUM_BREAK", 0.6, y=0, spread=3),
    S("move", 4, 40, vh=[0, 1.0, 0]), fx(40, "BLOCK", 80, "ENTITY_HOGLIN_ANGRY", 0.6, y=0, spread=3, block="CRIMSON_NYLIUM"),
    S("anim", 46, 28, name="charge"), fx(60, "CRIMSON_SPORE", 80, "ENTITY_HOGLIN_ATTACK", 0.6, y=0.7)]
DEATH["old_tusker"] = [S("flash", 0, 3, block="shroomlight"), fx(0, sound="ENTITY_HOGLIN_DEATH", pitch=0.5), S("anim", 0, 30, name="die_side"),
    fx(20, "CRIMSON_SPORE", 120, "BLOCK_FUNGUS_PLACE", 0.6, y=0.5, spread=3), S("swap", 30, block="crimson_nylium", order="up", stagger=30),
    S("scale", 62, 24, s=[1.3, 0.2, 1.3]), gone(86, 12)]

SPAWN["elder_eye"] = [S("shrink", 0, s=0), fx(0, "BUBBLE", 120, "ENTITY_ELDER_GUARDIAN_AMBIENT", 0.6, y=0.5, spread=3),
    S("pose", 6, 30, order="random", stagger=30), fx(30, "NAUTILUS", 80, "ENTITY_ELDER_GUARDIAN_CURSE", 0.7, y=0.6, spread=2),
    S("anim", 40, 22, name="spin")]
DEATH["elder_eye"] = [S("flash", 0, 3, block="orange_concrete"), fx(0, sound="ENTITY_ELDER_GUARDIAN_DEATH", pitch=0.6), S("anim", 0, 26, name="die_drop"),
    S("burst", 20, 10, power=3, up=2, tilt=180, rand=1, only="!head"), fx(30, "BUBBLE_POP", 120, "ENTITY_GUARDIAN_FLOP", 0.6, y=0.3, spread=3),
    S("shrink", 40, 20, s=0, only="head"), gone(64, 10)]

SPAWN["queen_bee"] = [S("move", 0, v=[0, 10, 0]), S("shrink", 0, s=0), fx(0, "FALLING_NECTAR", 60, "ENTITY_BEE_LOOP_AGGRESSIVE", 0.6, y=1, spread=2),
    S("pose", 4, 20, order="up", stagger=16), S("move", 6, 30, v=[0, -10, 0]), fx(36, "WAX_ON", 60, "ENTITY_BEE_POLLINATE", 0.6, y=0.6),
    S("anim", 40, 24, name="spin")]
DEATH["queen_bee"] = [S("flash", 0, 3, block="yellow_concrete"), fx(0, sound="ENTITY_BEE_DEATH", pitch=0.5), S("anim", 0, 26, name="die_drop"),
    fx(20, "DRIPPING_HONEY", 80, "BLOCK_HONEY_BLOCK_SLIDE", 0.6, y=0.4, spread=2), S("swap", 24, block="honey_block", order="up", stagger=20),
    S("scale", 46, 20, s=[1.4, 0.2, 1.4]), gone(68, 10)]

SPAWN["pillager_captain"] = [S("shrink", 0, s=0), fx(0, "CLOUD", 40, "EVENT_RAID_HORN", 0.9, y=0.2, spread=2),
    S("pose", 6, 6, order="up", stagger=26, only="!banner"), S("move", 20, vh=[0, 1.0, 0], only="banner"), S("pose", 34, 10, only="banner"),
    fx(44, "FIREWORK", 40, "ENTITY_FIREWORK_ROCKET_LAUNCH", 0.8, y=1.2), fx(50, "FLASH", 1, "ENTITY_FIREWORK_ROCKET_BLAST", 0.8, y=2),
    S("anim", 52, 26, name="roar")]
DEATH["pillager_captain"] = [S("flash", 0, 3, block="white_wool"), fx(0, sound="ENTITY_PILLAGER_DEATH", pitch=0.6), S("anim", 0, 28, name="die_back"),
    S("fling", 6, power=2, up=6, tilt=180, only="banner"), S("fling", 10, power=3, up=3, tilt=240, only="bow"),
    fx(24, "FIREWORK", 80, "ENTITY_FIREWORK_ROCKET_TWINKLE", 0.7, y=0.6, spread=2), S("burst", 34, 10, power=2, up=3, tilt=180, rand=1, only="!banner"),
    fx(36, "ITEM", 30, "ENTITY_ITEM_PICKUP", 0.6, y=0.4, item="EMERALD"), gone(58, 10)]

SPAWN["pale_watcher"] = [S("move", 0, vh=[0, -1.02, 0]), fx(0, "PALE_OAK_LEAVES", 80, "BLOCK_CREAKING_HEART_IDLE", 0.6, y=0.6, spread=3),
    S("move", 4, 60, vh=[0, 1.02, 0]), fx(30, "BLOCK", 80, "BLOCK_WOOD_BREAK", 0.6, y=0, spread=2, block="PALE_OAK_LOG"),
    S("light", 64, on=True, only="heart"), fx(66, sound="ENTITY_CREAKING_ACTIVATE", pitch=0.6), S("anim", 70, 28, name="roar")]
DEATH["pale_watcher"] = [S("flash", 0, 3, block="orange_concrete"), fx(0, sound="ENTITY_CREAKING_DEATH", pitch=0.6), S("shake", 0, 20),
    S("move", 10, 20, v=[0, 2.4, 1.4], only="heart"), S("shatter", 30, pieces=3, power=2, up=2, only="heart"), fx(30, "BLOCK", 60, "BLOCK_CREAKING_HEART_BREAK", 0.6, y=0.6, block="RESIN_BLOCK"),
    S("anim", 20, 30, name="die_front"), S("burst", 46, 12, power=1.5, up=3, tilt=90, rand=2, only="!heart"),
    fx(48, "PALE_OAK_LEAVES", 120, "BLOCK_WOOD_BREAK", 0.6, y=0.4, spread=3), gone(70, 12)]

SPAWN["weeping_ghast"] = [S("shrink", 0, s=0), fx(0, "WHITE_ASH", 120, "ENTITY_GHAST_AMBIENT", 0.5, y=0.8, spread=3),
    S("pose", 4, 30, only="head"), S("pose", 20, 20, order="down", stagger=16, only="tent"), fx(36, "SOUL", 40, "ENTITY_GHAST_SCREAM", 0.6, y=0.4),
    S("anim", 42, 22, name="raise")]
DEATH["weeping_ghast"] = [S("flash", 0, 4, block="red_concrete"), fx(0, sound="ENTITY_GHAST_DEATH", pitch=0.5),
    S("drop", 6, 16, tilt=60, rand=2, only="tent"), S("anim", 0, 26, name="die_drop"), S("swap", 20, block="light_gray_concrete", order="random", stagger=20),
    fx(30, "WHITE_ASH", 160, "ENTITY_GHAST_HURT", 0.4, y=0.4, spread=3), S("scale", 40, 24, s=[0.6, 0.6, 0.6], only="head"),
    fx(60, "SOUL", 60, "PARTICLE_SOUL_ESCAPE", 0.6, y=0.8), gone(66, 10)]

SPAWN["elder_sniffer"] = [S("move", 0, vh=[0, -1.02, 0]), fx(0, "BLOCK", 80, "ENTITY_SNIFFER_DIGGING", 0.6, y=0, spread=3, block="MOSS_BLOCK"),
    S("move", 4, 60, vh=[0, 1.02, 0]), fx(40, "HAPPY_VILLAGER", 40, "ENTITY_SNIFFER_SNIFFING", 0.6, y=1, spread=2),
    S("anim", 66, 28, name="howl"), fx(76, sound="ENTITY_SNIFFER_HAPPY", pitch=0.5)]
DEATH["elder_sniffer"] = [S("flash", 0, 3, block="moss_block"), fx(0, sound="ENTITY_SNIFFER_DEATH", pitch=0.5), S("anim", 0, 30, name="die_collapse"),
    fx(24, "SPORE_BLOSSOM_AIR", 120, "BLOCK_MOSS_PLACE", 0.6, y=0.6, spread=3), S("swap", 30, block="moss_block", order="up", stagger=30),
    S("scale", 64, 24, s=[1.3, 0.3, 1.3]), gone(90, 12)]

SPAWN["cinderheart"] = [S("move", 0, v=[0, 26, 0]), S("scale", 0, s=[0.7, 1.4, 0.7]), fx(0, "FLAME", 40, "ENTITY_MAGMA_CUBE_JUMP", 0.4, y=2),
    S("move", 2, 14, v=[0, -26, 0]), S("scale", 16, 4, s=[1.6, 0.5, 1.6]), fx(16, "LAVA", 80, "ENTITY_MAGMA_CUBE_SQUISH", 0.4, y=0, spread=3, ring=4),
    S("anim", 24, 20, name="hop"), fx(40, "FLAME", 60, "BLOCK_LAVA_POP", 0.6, y=0.6)]
DEATH["cinderheart"] = [S("flash", 0, 4, block="yellow_concrete"), fx(0, sound="ENTITY_MAGMA_CUBE_DEATH", pitch=0.4),
    S("burst", 6, 12, power=2.5, up=5, tilt=90, rand=1.5, only="slice"), S("light", 6, on=False, only="inner"),
    S("swap", 10, block="obsidian", only="inner"), fx(14, "LAVA", 100, "BLOCK_LAVA_EXTINGUISH", 0.5, y=0.4, spread=3),
    S("drop", 30, 12, tilt=40, rand=2, only="slice"), S("scale", 40, 20, s=[1.5, 0.2, 1.5], only="inner"), gone(66, 10)]

SPAWN["shulker_matriarch"] = [S("shrink", 0, s=0), fx(0, "PORTAL", 100, "ENTITY_SHULKER_TELEPORT", 0.6, y=0.4, spread=2),
    S("pose", 6, 16, only="core"), S("pose", 20, 16, only="lid"), S("pose", 30, 16, only="head"), fx(40, "END_ROD", 40, "ENTITY_SHULKER_OPEN", 0.6, y=0.8),
    S("pose", 44, 20, order="random", stagger=20, only="ring1"), S("anim", 60, 20, name="spin")]
DEATH["shulker_matriarch"] = [S("flash", 0, 3, block="purpur_block"), fx(0, sound="ENTITY_SHULKER_DEATH", pitch=0.6),
    S("fling", 4, power=2, up=6, tilt=180, only="lid"), S("burst", 8, 10, power=3, up=2, tilt=360, only="ring1"),
    S("shrink", 16, 16, s=0, only="head"), fx(18, "END_ROD", 80, "ENTITY_SHULKER_HURT_CLOSED", 0.6, y=0.5, spread=2),
    S("shatter", 34, pieces=3, power=2, up=2, only="core"), gone(54, 10)]

SPAWN["frostmaw"] = [S("move", 0, vh=[0, -1.02, 0]), fx(0, "SNOWFLAKE", 100, "BLOCK_POWDER_SNOW_BREAK", 0.6, y=0, spread=3),
    S("move", 4, 50, vh=[0, 1.02, 0]), fx(46, "BLOCK", 80, "ENTITY_POLAR_BEAR_WARNING", 0.6, y=0, spread=3, block="SNOW_BLOCK"),
    S("anim", 54, 30, name="rear"), fx(72, "SNOWFLAKE", 80, "ENTITY_POLAR_BEAR_WARNING", 0.5, y=0.8)]
DEATH["frostmaw"] = [S("flash", 0, 3, block="packed_ice"), fx(0, sound="ENTITY_POLAR_BEAR_DEATH", pitch=0.5), S("anim", 0, 30, name="die_side"),
    S("swap", 24, block="packed_ice", order="up", stagger=30), fx(30, "SNOWFLAKE", 120, "BLOCK_GLASS_BREAK", 0.6, y=0.5, spread=3),
    S("shatter", 60, pieces=3, power=2, up=3, order="random", stagger=16), gone(82, 10)]

SPAWN["bogmaw"] = [S("move", 0, v=[0, 18, -8]), fx(0, "SPLASH", 60, "ENTITY_FROG_LONG_JUMP", 0.5, y=0, spread=2),
    S("move", 2, 16, v=[0, -18, 8]), S("scale", 18, 4, s=[1.3, 0.7, 1.3]), fx(18, "BLOCK", 80, "ENTITY_FROG_STEP", 0.5, y=0, spread=3, block="MUD"),
    S("pose", 24, 6), S("anim", 30, 24, name="bite"), fx(36, sound="ENTITY_FROG_TONGUE", pitch=0.5)]
DEATH["bogmaw"] = [S("flash", 0, 3, block="orange_terracotta"), fx(0, sound="ENTITY_FROG_DEATH", pitch=0.5), S("anim", 0, 28, name="die_side"),
    S("fling", 8, power=2, up=4, tilt=180, only="tongue"), fx(20, "SPLASH", 120, "BLOCK_MUD_BREAK", 0.6, y=0.2, spread=3),
    S("scale", 36, 24, s=[1.4, 0.15, 1.4], only="!tongue"), gone(64, 10)]

SPAWN["ramthunder"] = [S("move", 0, v=[0, 10, -14]), fx(0, "SNOWFLAKE", 40, "ENTITY_GOAT_SCREAMING_AMBIENT", 0.6, y=0.6),
    S("move", 2, 18, v=[0, -10, 14]), fx(20, "BLOCK", 80, "ENTITY_GOAT_STEP", 0.5, y=0, spread=3, block="STONE"),
    S("anim", 26, 30, name="rear"), fx(44, sound="BLOCK_BELL_USE", pitch=0.6)]
DEATH["ramthunder"] = [S("flash", 0, 3), fx(0, sound="ENTITY_GOAT_SCREAMING_DEATH", pitch=0.6), S("anim", 0, 30, name="die_side"),
    fx(12, sound="BLOCK_BELL_USE", pitch=0.4), S("burst", 30, 10, power=2, up=4, tilt=180, rand=1.2), fx(32, "BLOCK", 120, "BLOCK_STONE_BREAK", 0.6, y=0.4, spread=2, block="SNOW_BLOCK"),
    S("drop", 44, 14, tilt=90, rand=2), gone(72, 12)]

# ------------------------------------------------------------------------------------------------ chapters

SPAWN["nightwing"] = [S("move", 0, v=[0, 20, -20]), fx(0, "WHITE_ASH", 60, "ENTITY_PHANTOM_SWOOP", 0.6, y=0.6, spread=3),
    S("move", 2, 30, v=[0, -20, 20]), S("anim", 2, 30, name="walk"), fx(32, "SMOKE", 60, "ENTITY_PHANTOM_AMBIENT", 0.5, y=0.4),
    S("anim", 34, 26, name="howl")]
DEATH["nightwing"] = [S("flash", 0, 3, block="lime_concrete"), fx(0, sound="ENTITY_PHANTOM_DEATH", pitch=0.5),
    S("fling", 4, power=3, up=4, tilt=240, only="wingL"), S("fling", 6, power=3, up=4, tilt=240, only="wingR"),
    S("anim", 0, 26, name="die_side"), fx(20, "WHITE_ASH", 120, "ENTITY_PHANTOM_HURT", 0.5, y=0.5, spread=3), S("drop", 24, 14, tilt=60, rand=2), gone(50, 10)]

SPAWN["deep_mother"] = [S("move", 0, vh=[0, -1.1, 0]), fx(0, "GLOW_SQUID_INK", 80, "ENTITY_GLOW_SQUID_SQUIRT", 0.5, y=0, spread=3),
    S("move", 4, 50, vh=[0, 1.1, 0]), fx(30, "BUBBLE_COLUMN_UP", 120, "ENTITY_GLOW_SQUID_AMBIENT", 0.5, y=0.3, spread=3),
    S("anim", 56, 20, name="raise")]
DEATH["deep_mother"] = [S("flash", 0, 3, block="light_blue_concrete"), fx(0, sound="ENTITY_GLOW_SQUID_DEATH", pitch=0.5), S("anim", 0, 26, name="die_drop"),
    S("light", 10, on=False, only="lit"), fx(10, "GLOW_SQUID_INK", 200, "ENTITY_GLOW_SQUID_SQUIRT", 0.4, y=0.5, spread=3),
    S("drop", 20, 16, tilt=40, rand=2, only="tent"), S("scale", 40, 20, s=[1.3, 0.2, 1.3], only="head"), gone(64, 10)]

SPAWN["bellwarden"] = [S("shrink", 0, s=0), S("pose", 0, 2, only="bell"), fx(0, sound="BLOCK_BELL_USE", pitch=0.5),
    fx(16, sound="BLOCK_BELL_USE", pitch=0.5), fx(16, "SOUL", 40, "BLOCK_BELL_RESONATE", 0.6, y=0.8),
    S("pose", 20, 4, order="up", stagger=30, only="!bell"), fx(52, "BLOCK", 60, "BLOCK_BONE_BLOCK_PLACE", 0.6, y=0.3, block="BONE_BLOCK"),
    S("anim", 56, 28, name="roar")]
DEATH["bellwarden"] = [S("flash", 0, 3, block="gold_block"), fx(0, sound="BLOCK_BELL_USE", pitch=0.3), S("anim", 0, 28, name="die_front"),
    S("drop", 10, 16, tilt=30, only="bell"), fx(26, sound="BLOCK_BELL_RESONATE", pitch=0.4), S("burst", 30, 10, power=2, up=4, tilt=180, rand=1.2, only="!bell"),
    fx(32, "BLOCK", 120, "BLOCK_BONE_BLOCK_BREAK", 0.6, y=0.4, spread=2, block="BONE_BLOCK"), S("drop", 44, 14, tilt=90, rand=2, only="!bell"), gone(76, 12)]

SPAWN["the_shrieker"] = [S("move", 0, vh=[0, -1.05, 0]), fx(0, "SCULK_CHARGE_POP", 80, "BLOCK_SCULK_SHRIEKER_SHRIEK", 0.6, y=0, spread=3),
    S("move", 4, 50, vh=[0, 1.05, 0]), S("light", 56, on=True, only="lit"), fx(58, "SHRIEK", 4, "BLOCK_SCULK_SHRIEKER_SHRIEK", 0.6, y=0.8, shriek=0),
    S("anim", 60, 26, name="howl")]
DEATH["the_shrieker"] = [S("flash", 0, 3, block="cyan_concrete"), fx(0, sound="BLOCK_SCULK_SHRIEKER_SHRIEK", pitch=0.4), S("anim", 0, 30, name="die_collapse"),
    S("light", 20, on=False, only="lit"), S("swap", 24, block="sculk", order="up", stagger=30),
    S("scale", 56, 24, s=[1.4, 0.05, 1.4]), fx(58, "SCULK_CHARGE_POP", 120, "BLOCK_SCULK_SPREAD", 0.6, y=0, spread=3), gone(80, 10)]

# ------------------------------------------------------------------------------------------------ seasonal

SPAWN["frostbottom"] = [S("shrink", 0, s=0), fx(0, "SNOWFLAKE", 80, "BLOCK_SNOW_PLACE", 0.6, y=0.2, spread=2),
    S("pose", 4, 8, only="leg"), S("pose", 14, 8, only="hips"), S("pose", 24, 8, only="body"), fx(28, sound="BLOCK_SNOW_PLACE", pitch=0.6),
    S("pose", 32, 6, only="arm"), S("move", 38, vh=[0, 1.2, 0], only="head"), S("pose", 40, 12, only="head"), S("pose", 52, 10, only="hat"),
    fx(60, "SNOWFLAKE", 60, "ENTITY_SNOW_GOLEM_AMBIENT", 0.6, y=0.9), S("anim", 62, 24, name="roar")]
DEATH["frostbottom"] = [S("flash", 0, 3, block="snow_block"), fx(0, sound="ENTITY_SNOW_GOLEM_DEATH", pitch=0.6),
    S("fling", 4, power=2, up=6, tilt=360, only="hat"), S("fling", 8, power=3, up=4, tilt=240, only="head"),
    S("anim", 10, 26, name="die_back"), fx(20, "SNOWFLAKE", 120, "BLOCK_SNOW_BREAK", 0.6, y=0.5, spread=3),
    S("scale", 30, 30, s=[1.6, 0.05, 1.6], only="!hat"), fx(50, "SPLASH", 80, "BLOCK_SNOW_BREAK", 0.6, y=0, spread=3), gone(66, 10)]

SPAWN["bogged_hunter"] = [S("move", 0, vh=[0, -1.02, 0]), fx(0, "SPORE_BLOSSOM_AIR", 60, "ENTITY_BOGGED_AMBIENT", 0.5, y=0, spread=2),
    S("move", 4, 40, vh=[0, 1.02, 0]), fx(30, "BLOCK", 60, "BLOCK_MUD_BREAK", 0.6, y=0, spread=2, block="MUD"),
    S("light", 46, on=True, only="lit"), S("anim", 48, 26, name="cast")]
DEATH["bogged_hunter"] = [S("flash", 0, 3, block="lime_concrete"), fx(0, sound="ENTITY_BOGGED_DEATH", pitch=0.6), S("anim", 0, 28, name="die_back"),
    S("drop", 10, 12, tilt=60, only="bow"), fx(20, "SPORE_BLOSSOM_AIR", 120, "BLOCK_FUNGUS_BREAK", 0.6, y=0.6, spread=2),
    S("burst", 30, 10, power=1.5, up=3, tilt=180, rand=1.2, only="!bow"), S("drop", 42, 14, tilt=90, rand=2, only="!bow"), gone(72, 12)]

SPAWN["iron_tusk"] = [S("move", 0, v=[0, 0, -12]), S("anim", 0, 30, name="walk"), fx(0, "CRIMSON_SPORE", 40, "ENTITY_ZOGLIN_ANGRY", 0.6, y=0.4, spread=2),
    S("move", 2, 26, v=[0, 0, 12]), fx(20, "BLOCK", 80, "BLOCK_CHAIN_BREAK", 0.6, y=0.2, spread=2, block="IRON_BLOCK"),
    S("anim", 30, 28, name="charge"), fx(44, sound="ENTITY_ZOGLIN_ATTACK", pitch=0.6)]
DEATH["iron_tusk"] = [S("flash", 0, 3, block="iron_block"), fx(0, sound="ENTITY_ZOGLIN_DEATH", pitch=0.5), S("anim", 0, 30, name="die_side"),
    S("fling", 14, power=2, up=4, tilt=200, only="iron_block"), fx(20, "BLOCK", 100, "BLOCK_ANVIL_LAND", 0.5, y=0.2, spread=2, block="IRON_BLOCK"),
    S("swap", 34, block="rooted_dirt", order="up", stagger=24, only="!iron_block"), S("shatter", 60, pieces=3, power=2, up=2, only="!iron_block"), gone(80, 12)]

SPAWN["ember_knight"] = [S("move", 0, vh=[0, -1.02, 0]), fx(0, "SOUL_FIRE_FLAME", 60, "ENTITY_WITHER_SKELETON_AMBIENT", 0.5, y=0, spread=2),
    S("move", 4, 46, vh=[0, 1.02, 0]), S("light", 50, on=True, only="lit"), fx(50, "LAVA", 40, "BLOCK_BLACKSTONE_PLACE", 0.6, y=0.3),
    S("anim", 54, 30, name="sweep"), fx(64, "SWEEP_ATTACK", 4, "ENTITY_PLAYER_ATTACK_SWEEP", 0.5, y=0.6, spread=2)]
DEATH["ember_knight"] = [S("flash", 0, 3, block="orange_concrete"), fx(0, sound="ENTITY_WITHER_SKELETON_DEATH", pitch=0.5), S("anim", 0, 28, name="die_kneel"),
    S("drop", 12, 14, tilt=80, only="sword"), S("light", 18, on=False, only="lit"), fx(20, "LARGE_SMOKE", 80, "BLOCK_FIRE_EXTINGUISH", 0.5, y=0.6),
    S("swap", 26, block="coal_block", order="up", stagger=24, only="!sword"), S("burst", 54, 10, power=1.5, up=3, tilt=180, rand=1.2, only="!sword"),
    fx(56, "ASH", 120, "BLOCK_BASALT_BREAK", 0.6, y=0.4, spread=2), gone(78, 12)]
