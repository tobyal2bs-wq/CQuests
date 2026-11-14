"""How every boss arrives and how it dies. Each one is written for that boss: its own pieces move first
(a crown floats down, a head is thrown, the sack opens), its own particles and sounds, its own rig move.
Times are ticks (20 a second); distances are blocks; vh means a fraction of the boss's height.
"only" picks the blocks a step moves: a bone name prefix (head, armL, sword, ring1), a block id, lit, unlit
or !something for everything else. Every death has a flash and ends with the blocks gone."""


def S(op, at=0, dur=0, **kw):
    d = {"op": op, "at": at}
    if dur:
        d["dur"] = dur
    d.update(kw)
    return d


def fx(at, particle=None, count=30, sound=None, pitch=1.0, y=0.5, spread=1.0, **kw):
    d = {"op": "fx", "at": at, "y": y, "spread": spread}
    if particle:
        d["particle"], d["count"] = particle, count
    if sound:
        d["sound"], d["pitch"] = sound, pitch
    d.update(kw)
    return d


def gone(at, dur=12, order="random"):
    return S("shrink", at, dur, s=0, order=order, stagger=dur)


SPAWN, DEATH = {}, {}

# ------------------------------------------------------------------------------------------------ general

SPAWN["slagheart"] = [S("move", 0, vh=[0, -1.05, 0]), fx(0, "LAVA", 30, "BLOCK_LAVA_POP", 0.5, y=0, spread=2, ring=3),
    S("move", 4, 40, vh=[0, 1.05, 0]), S("light", 4, on=True, only="redstone_block"), fx(20, "FLAME", 50, "BLOCK_STONE_BREAK", 0.5, y=0.1, spread=2.5),
    fx(44, "EXPLOSION", 2, "ENTITY_IRON_GOLEM_REPAIR", 0.5), S("anim", 46, 28, name="slam"), fx(62, "BLOCK", 120, "ENTITY_GENERIC_EXPLODE", 0.6, y=0, spread=3, block="MAGMA_BLOCK")]
DEATH["slagheart"] = [S("anim", 0, 28, name="die_front"), S("flash", 2, 3, block="orange_concrete", only="lit"), fx(2, "LAVA", 40, "ENTITY_IRON_GOLEM_DEATH", 0.5),
    S("swap", 20, block="obsidian", only="redstone_block"), S("swap", 22, block="basalt", only="orange_concrete"), fx(26, "LARGE_SMOKE", 60, "BLOCK_FIRE_EXTINGUISH", 0.6),
    S("shatter", 40, pieces=3, power=2, up=2, order="up", stagger=24), fx(44, "BLOCK", 120, "BLOCK_STONE_BREAK", 0.5, y=0.2, spread=2, block="ANDESITE"), gone(70)]

SPAWN["warlord_gruk"] = [S("scale", 0, s=[1.5, 0.05, 1.5]), S("swap", 0, block="gold_block"), fx(1, "WAX_ON", 50, "BLOCK_METAL_PLACE", 0.6, y=0, spread=2),
    S("pose", 4, 30, order="up", stagger=10), S("swap", 38, block="", order="up", stagger=16),
    fx(40, "WAX_ON", 60, "ENTITY_PIGLIN_BRUTE_ANGRY", 0.7), S("anim", 56, 26, name="stomp"), fx(70, "BLOCK", 80, "ENTITY_GENERIC_EXPLODE", 0.8, y=0, spread=3, block="GOLD_BLOCK")]
DEATH["warlord_gruk"] = [S("anim", 0, 28, name="die_back"), S("flash", 0, 3), S("swap", 4, block="gold_block", order="down", stagger=20),
    fx(24, "WAX_ON", 60, "ENTITY_PIGLIN_BRUTE_DEATH", 0.6), S("fling", 30, power=5, up=4, tilt=200, only="maul"),
    S("burst", 32, 10, power=2, up=6, tilt=180, rand=1.5, only="!maul"), fx(32, "EXPLOSION", 3, "ENTITY_GENERIC_EXPLODE", 1.2),
    S("drop", 42, 12, tilt=90, rand=3, only="!maul"), fx(52, "WAX_ON", 60, "BLOCK_CHAIN_PLACE", 0.6, y=0, spread=4), gone(76, 16)]

SPAWN["grand_augur"] = [S("shrink", 0, s=0), S("pose", 2, 10, only="gem"), fx(2, "END_ROD", 30, "BLOCK_AMETHYST_BLOCK_CHIME", 1.4, y=0.9),
    fx(10, "ENCHANT", 120, "ENTITY_EVOKER_PREPARE_SUMMON", 1.0, y=0.4, spread=2, ring=3), S("pose", 14, 3, order="up", stagger=30, only="!crown"),
    S("move", 14, vh=[0, 0.8, 0], only="crown"), S("pose", 46, 14, only="crown"), fx(58, "TOTEM_OF_UNDYING", 60, "ENTITY_EVOKER_CAST_SPELL", 0.8, y=0.8),
    S("anim", 60, 30, name="cast")]
DEATH["grand_augur"] = [S("flash", 0, 4, block="gold_block"), S("anim", 0, 30, name="die_kneel"), fx(0, "ENCHANT", 80, "ENTITY_EVOKER_DEATH", 0.8),
    S("move", 10, 30, v=[0, 4, 0], only="crown"), S("spin", 10, 30, deg=360, only="crown"), S("fling", 20, power=3, up=5, only="staff"),
    S("move", 30, 20, v=[0, 6, 0], only="gem"), fx(46, "FLASH", 1, "BLOCK_AMETHYST_BLOCK_BREAK", 0.6, y=1.0), S("shatter", 48, pieces=4, power=3, up=2, only="gem"),
    S("shrink", 44, 10, s=0, only="crown"), S("scale", 50, 20, s=[1.6, 0.05, 1.6], only="!gem"), fx(52, "WITCH", 80, "ENTITY_VEX_DEATH", 0.8, y=0.1, spread=2), gone(76, 8)]

SPAWN["crimson_ronin"] = [S("shrink", 0, s=0), fx(0, "CHERRY_LEAVES", 120, "BLOCK_CHERRY_LEAVES_BREAK", 0.8, y=0.6, spread=3), S("pose", 8, 2, order="random", stagger=24),
    fx(12, "CRIMSON_SPORE", 60, "ITEM_ARMOR_EQUIP_IRON", 0.7), fx(34, "SWEEP_ATTACK", 6, "ENTITY_PLAYER_ATTACK_SWEEP", 0.6, y=0.6, spread=2),
    S("anim", 36, 26, name="sweep"), fx(60, "FLAME", 40, "ENTITY_RAVAGER_ROAR", 1.3, y=0.9)]
DEATH["crimson_ronin"] = [S("anim", 0, 24, name="die_kneel"), S("flash", 0, 3, block="red_concrete"), fx(0, "CHERRY_LEAVES", 100, "ENTITY_RAVAGER_DEATH", 1.2, spread=3),
    S("drop", 20, 10, tilt=40, only="club"), fx(28, sound="BLOCK_BELL_USE", pitch=0.5),
    S("burst", 40, 16, power=4, up=3, tilt=90, rand=2, order="up", stagger=20), fx(42, "CHERRY_LEAVES", 160, "BLOCK_CHERRY_LEAVES_FALL", 0.6, y=0.8, spread=4), gone(66)]

SPAWN["thunderback"] = [S("move", 0, v=[0, 24, 0]), S("pose", 2, 14), fx(14, "EXPLOSION_EMITTER", 1, "ENTITY_GENERIC_EXPLODE", 0.6, y=0, ring=5),
    fx(16, "BLOCK", 120, "ENTITY_RAVAGER_STUNNED", 0.8, y=0, spread=3, block="DIRT"), S("anim", 20, 30, name="roar"),
    fx(28, sound="ENTITY_LIGHTNING_BOLT_THUNDER", pitch=1.4, lightning=True), fx(30, "ELECTRIC_SPARK", 80, None, y=0.6, spread=2)]
DEATH["thunderback"] = [S("anim", 0, 26, name="die_back"), S("flash", 0, 4), fx(0, sound="ENTITY_RAVAGER_DEATH", pitch=1.4),
    fx(20, "ELECTRIC_SPARK", 100, "ENTITY_LIGHTNING_BOLT_IMPACT", 0.8, lightning=True), S("light", 24, on=True),
    S("drop", 30, 10, tilt=60, rand=1.4, order="down", stagger=20), fx(40, "CLOUD", 60, "ENTITY_PANDA_SNEEZE", 0.5, y=0.1, spread=2), gone(62)]

SPAWN["gorehorn"] = [S("move", 0, v=[0, 0, -14]), S("pose", 0, 22), fx(0, "BLOCK", 30, "ENTITY_RAVAGER_STEP", 0.6, y=0, spread=1, block="DIRT"),
    fx(10, "BLOCK", 30, "ENTITY_RAVAGER_STEP", 0.6, y=0, spread=1, block="DIRT"), fx(22, "EXPLOSION", 3, "ENTITY_RAVAGER_ROAR", 0.6, y=0.3),
    S("anim", 24, 28, name="roar"), fx(30, "CAMPFIRE_COSY_SMOKE", 20, None, y=0.7, spread=0.4)]
DEATH["gorehorn"] = [S("anim", 0, 26, name="die_front"), S("flash", 0, 3), fx(0, sound="ENTITY_RAVAGER_DEATH", pitch=0.7),
    S("fling", 18, power=4, up=3, tilt=220, only="axe"), fx(26, "BLOCK", 120, "BLOCK_ANVIL_LAND", 0.4, y=0, spread=3, block="DIRT"),
    S("move", 34, 30, v=[0, -2.4, 0], order="random", stagger=16), fx(50, "CAMPFIRE_COSY_SMOKE", 30, "BLOCK_GRAVEL_BREAK", 0.6, y=0), gone(70)]

SPAWN["abyssal_eye"] = [S("move", 0, vh=[0, -0.9, 0]), S("light", 0, on=True), fx(0, "BUBBLE_COLUMN_UP", 90, "ENTITY_ELDER_GUARDIAN_AMBIENT", 0.6, y=0, spread=2),
    S("move", 4, 40, vh=[0, 0.9, 0]), S("spin", 4, 40, deg=360), fx(30, "NAUTILUS", 80, "ENTITY_GUARDIAN_ATTACK", 0.6, y=0.6, spread=2),
    S("light", 46), fx(48, "SQUID_INK", 30, "ENTITY_ELDER_GUARDIAN_CURSE", 0.8, y=0.6), S("anim", 50, 24, name="pulse")]
DEATH["abyssal_eye"] = [S("flash", 0, 4, block="sea_lantern"), fx(0, "BUBBLE_POP", 80, "ENTITY_ELDER_GUARDIAN_DEATH", 0.8),
    S("anim", 0, 26, name="die_drop"), S("swap", 18, block="gray_concrete", only="lit"), S("burst", 30, 14, power=4, up=1, tilt=120, only="ring"),
    S("drop", 30, 14, tilt=110, rand=0.6, only="!ring"), fx(34, "SQUID_INK", 60, "ENTITY_GUARDIAN_FLOP", 0.7, y=0.1, spread=2), gone(60)]

SPAWN["overgrowth"] = [S("scale", 0, s=[0.2, 0.05, 0.2]), fx(0, "SPORE_BLOSSOM_AIR", 60, "BLOCK_ROOTED_DIRT_BREAK", 0.6, y=0, spread=2),
    S("scale", 4, 40, s=[5, 20, 5]), S("pose", 44, 8), fx(20, "HAPPY_VILLAGER", 50, "BLOCK_AZALEA_LEAVES_PLACE", 0.8, y=0.5, spread=2),
    fx(46, "CHERRY_LEAVES", 80, "BLOCK_BIG_DRIPLEAF_TILT_DOWN", 0.6, y=0.9, spread=2), S("anim", 50, 30, name="roar")]
DEATH["overgrowth"] = [S("anim", 0, 24, name="die_kneel"), S("flash", 0, 3, block="lime_concrete"), fx(0, "SPORE_BLOSSOM_AIR", 80, "BLOCK_MOSS_BREAK", 0.6),
    S("swap", 10, block="dirt", order="up", stagger=30), S("drop", 28, 12, tilt=40, rand=1.2, order="down", stagger=20),
    S("scale", 52, 20, s=[1.4, 0.05, 1.4]), fx(52, "HAPPY_VILLAGER", 60, "BLOCK_GRASS_PLACE", 0.6, y=0, spread=2), gone(76, 8)]

SPAWN["prism_sentinel"] = [S("burst", 0, power=10, up=6, tilt=200, rand=3), fx(0, "END_ROD", 60, "BLOCK_AMETHYST_CLUSTER_PLACE", 1.4, spread=4),
    S("pose", 4, 18, order="in", stagger=30), fx(20, "WAX_OFF", 50, "BLOCK_AMETHYST_BLOCK_RESONATE", 1.0), S("light", 50, on=True, only="ring1"),
    fx(52, "END_ROD", 80, "BLOCK_BEACON_ACTIVATE", 1.3, y=0.7), S("anim", 54, 28, name="cast")]
DEATH["prism_sentinel"] = [S("flash", 0, 3, block="diamond_block"), S("anim", 0, 20, name="die_kneel"), fx(0, sound="BLOCK_AMETHYST_BLOCK_BREAK", pitch=0.6),
    S("shake", 14, 16), S("shatter", 30, pieces=4, power=4, up=3, order="out", stagger=12), fx(32, "END_ROD", 120, "BLOCK_GLASS_BREAK", 0.8, spread=3), gone(54)]

SPAWN["tiki_warden"] = [S("shrink", 0, s=0, only="!head"), S("move", 0, v=[0, 10, 0], only="head"), fx(0, "FLAME", 40, "BLOCK_NOTE_BLOCK_BASEDRUM", 0.6, y=1.2, ring=3),
    S("move", 6, 20, v=[0, -10, 0], only="head"), fx(8, sound="BLOCK_NOTE_BLOCK_BASEDRUM", pitch=0.7), fx(16, sound="BLOCK_NOTE_BLOCK_BASEDRUM", pitch=0.6),
    S("pose", 26, 3, order="up", stagger=20), fx(26, "FLAME", 30, "BLOCK_NOTE_BLOCK_BASEDRUM", 0.5, y=0), fx(46, "LAVA", 20, "ENTITY_RAVAGER_ROAR", 1.1, y=0.9), S("anim", 48, 26, name="stomp")]
DEATH["tiki_warden"] = [S("anim", 0, 24, name="die_back"), S("flash", 0, 3, block="orange_concrete"), fx(0, "FLAME", 50, "BLOCK_NOTE_BLOCK_BASEDRUM", 0.4),
    S("fling", 24, power=3, up=5, tilt=360, only="head"), S("drop", 26, 12, tilt=90, rand=1, only="!head"), fx(30, "CAMPFIRE_COSY_SMOKE", 30, "BLOCK_WOOD_BREAK", 0.6, y=0.2),
    S("swap", 40, block="coal_block", only="lit"), fx(42, "SMOKE", 60, "BLOCK_FIRE_EXTINGUISH", 0.8, y=0.1), gone(70)]

SPAWN["hollow_king"] = [S("move", 0, vh=[0, -1.05, 0]), fx(0, "SOUL", 60, "ENTITY_WITHER_SPAWN", 0.5, y=0, spread=2.5, ring=4),
    S("pose", 4, 40, order="up", stagger=20), fx(20, "SOUL_FIRE_FLAME", 60, "BLOCK_SOUL_SAND_BREAK", 0.5, y=0.2), S("light", 50, on=True, only="light_blue_concrete"),
    fx(50, "SOUL", 80, "ENTITY_WITHER_SKELETON_AMBIENT", 0.4, y=0.9), S("anim", 52, 30, name="roar")]
DEATH["hollow_king"] = [S("anim", 0, 30, name="die_kneel"), S("flash", 0, 3, block="light_blue_concrete"), fx(0, "SOUL", 50, "ENTITY_WITHER_SKELETON_DEATH", 0.5),
    S("drop", 26, 10, tilt=80, only="sword"), S("move", 30, 20, v=[0, 3, 0], only="lit"), S("shrink", 50, 6, s=0, only="lit"),
    S("drop", 34, 14, tilt=80, rand=0.8, order="down", stagger=30, only="unlit"), fx(56, "SOUL", 100, "BLOCK_SOUL_SAND_BREAK", 0.5, y=0.9, spread=0.6), gone(80, 14)]

SPAWN["broodmother"] = [S("move", 0, v=[0, 20, 0]), S("pose", 0, 30), fx(0, "ITEM_COBWEB", 40, "ENTITY_SPIDER_AMBIENT", 0.5, y=1.6, spread=1),
    fx(10, "ITEM_COBWEB", 40, None, y=1.2, spread=1), fx(30, "BLOCK", 80, "ENTITY_SPIDER_STEP", 0.4, y=0, spread=3, block="COBWEB"),
    S("anim", 32, 28, name="rearup"), fx(40, "SPORE_BLOSSOM_AIR", 40, "ENTITY_SPIDER_HURT", 0.5, y=0.5)]
DEATH["broodmother"] = [S("anim", 0, 32, name="die_curl"), S("flash", 0, 3, block="lime_concrete"), fx(0, sound="ENTITY_SPIDER_DEATH", pitch=0.4),
    S("burst", 34, 12, power=3, up=2, tilt=120, only="abdomen"), fx(34, "ITEM_SLIME", 80, "BLOCK_SLIME_BLOCK_BREAK", 0.6, y=0.3, spread=2),
    S("drop", 44, 10, tilt=40, only="!abdomen"), fx(50, "ITEM_COBWEB", 60, "BLOCK_WOOL_BREAK", 0.5, y=0.1, spread=2), gone(70)]

SPAWN["ironhide_behemoth"] = [S("move", 0, v=[0, 28, 0]), S("pose", 2, 16), fx(18, "EXPLOSION_EMITTER", 2, "ENTITY_GENERIC_EXPLODE", 0.5, y=0, ring=6),
    fx(18, "BLOCK", 120, "ENTITY_RAVAGER_STUNNED", 0.6, y=0, spread=4, block="DIRT"), S("shake", 20, 16), S("anim", 36, 30, name="howl")]
DEATH["ironhide_behemoth"] = [S("anim", 0, 30, name="die_collapse"), S("flash", 0, 3), fx(14, "BLOCK", 100, "ENTITY_RAVAGER_DEATH", 0.6, y=0, spread=3, block="DIRT"),
    S("burst", 34, 14, power=4, up=2, tilt=120, rand=1, only="iron_block"), fx(34, "EXPLOSION", 4, "BLOCK_ANVIL_LAND", 0.6),
    S("move", 50, 40, v=[0, -3, 0]), fx(60, "CAMPFIRE_COSY_SMOKE", 20, "ENTITY_RAVAGER_STUNNED", 0.5, y=0.2), gone(80, 10)]

SPAWN["fenrir"] = [S("shrink", 0, s=0), fx(0, "SNOWFLAKE", 120, "ENTITY_WOLF_HOWL", 0.5, y=0.6, spread=4), S("pose", 6, 2, order="random", stagger=40),
    fx(20, "WHITE_ASH", 60, "BLOCK_POWDER_SNOW_PLACE", 0.6), fx(46, "SNOWFLAKE", 80, "ENTITY_WOLF_GROWL", 0.4, y=0.3), S("anim", 48, 30, name="howl")]
DEATH["fenrir"] = [S("anim", 0, 28, name="die_side"), S("flash", 0, 3, block="light_blue_concrete"), fx(0, sound="ENTITY_WOLF_DEATH", pitch=0.4),
    S("swap", 20, block="packed_ice", order="up", stagger=20), fx(24, "SNOWFLAKE", 80, "BLOCK_GLASS_PLACE", 0.6), S("shatter", 46, pieces=3, power=3, up=2, order="random", stagger=16),
    fx(48, "ITEM_SNOWBALL", 80, "BLOCK_GLASS_BREAK", 0.5, spread=2), gone(70)]

SPAWN["tide_tyrant"] = [S("move", 0, vh=[0, -1.1, 0]), S("spin", 0, deg=-150), fx(1, "BUBBLE_POP", 80, "ENTITY_ELDER_GUARDIAN_CURSE", 0.7, y=0, spread=3, ring=3),
    S("move", 4, 30, vh=[0, 1.1, 0]), S("spin", 4, 30, deg=150), S("pose", 34, 10), fx(20, "SPLASH", 120, "ENTITY_GENERIC_SPLASH", 0.6, y=0, spread=3),
    fx(46, "BUBBLE_COLUMN_UP", 60, "ENTITY_DROWNED_AMBIENT_WATER", 0.5), S("anim", 46, 28, name="cast")]
DEATH["tide_tyrant"] = [S("anim", 0, 28, name="die_back"), S("flash", 0, 3, block="cyan_concrete"), fx(8, "BUBBLE_POP", 60, "ENTITY_DROWNED_DEATH", 0.6, y=0.2, spread=2),
    S("drop", 14, 10, tilt=60, only="trident"), S("move", 28, 40, v=[0, -5, 0], only="!trident"), S("spin", 28, 40, deg=200, only="!trident"),
    fx(30, "BUBBLE_COLUMN_UP", 80, "ENTITY_GENERIC_SPLASH", 0.5, y=0, spread=2.5), fx(50, "SPLASH", 120, "BLOCK_BUBBLE_COLUMN_WHIRLPOOL_INSIDE", 0.6, y=0, spread=3), gone(68, 6)]

SPAWN["void_walker"] = [S("shrink", 0, s=0), S("pose", 2, 1), S("move", 6, 1, v=[4, 0, 2]), fx(6, "REVERSE_PORTAL", 50, "ENTITY_ENDERMAN_TELEPORT", 0.5),
    S("move", 12, 1, v=[-8, 0, -3]), fx(12, "REVERSE_PORTAL", 50, "ENTITY_ENDERMAN_TELEPORT", 0.7),
    S("move", 18, 1, v=[3, 0, 5]), fx(18, "REVERSE_PORTAL", 50, "ENTITY_ENDERMAN_TELEPORT", 0.9),
    S("pose", 24, 1), fx(24, "PORTAL", 120, "ENTITY_ENDERMAN_SCREAM", 0.6, spread=1.5), S("anim", 26, 28, name="roar")]
DEATH["void_walker"] = [S("flash", 0, 3, block="magenta_concrete"), S("toward", 0, 14, y=0.55, k=1), S("spin", 0, 14, deg=150), fx(0, "REVERSE_PORTAL", 80, "ENTITY_ENDERMAN_DEATH", 0.6, y=0.55),
    S("shrink", 14, 6, s=0.1), fx(20, "FLASH", 1, "ENTITY_ENDERMAN_TELEPORT", 0.5, y=0.55),
    S("burst", 20, 8, power=7, up=0, tilt=200, rand=1), fx(20, "PORTAL", 200, "ENTITY_ENDER_EYE_DEATH", 0.6, y=0.55, spread=2), S("shrink", 28, 4, s=0)]

SPAWN["storm_herald"] = [S("shrink", 0, s=0), fx(2, sound="ENTITY_LIGHTNING_BOLT_THUNDER", pitch=1.2, lightning=True),
    S("pose", 4, 4, order="up", part=[0, 0.33]), fx(14, sound="ENTITY_LIGHTNING_BOLT_IMPACT", lightning=True),
    S("pose", 16, 4, order="up", part=[0.33, 0.66]), fx(26, "ELECTRIC_SPARK", 80, "ENTITY_LIGHTNING_BOLT_THUNDER", 0.8, lightning=True),
    S("pose", 28, 4, order="up", part=[0.66, 1]), S("anim", 34, 30, name="raise")]
DEATH["storm_herald"] = [S("flash", 0, 3, block="yellow_concrete"), fx(0, sound="ENTITY_LIGHTNING_BOLT_THUNDER", lightning=True), S("move", 0, 20, v=[0, 3, 0]), S("light", 0, on=True),
    fx(10, "ELECTRIC_SPARK", 80, "ENTITY_EVOKER_DEATH", 0.7, lightning=True), S("spin", 20, 10, deg=140), S("move", 20, 10, v=[0, 2, 0]),
    S("spin", 30, 10, deg=140), fx(30, sound="ENTITY_LIGHTNING_BOLT_IMPACT", lightning=True), S("burst", 40, 12, power=5, up=6, tilt=180, rand=2),
    S("shrink", 52, 6, s=0), fx(52, "FIREWORK", 80, "ENTITY_FIREWORK_ROCKET_TWINKLE", 0.8, y=1.2)]

SPAWN["pharaoh"] = [S("swap", 0, block="sand"), S("move", 0, vh=[0, -1.0, 0]), S("scale", 0, s=[0.2, 1, 0.2]),
    fx(1, "FALLING_DUST", 80, "BLOCK_SAND_BREAK", 0.5, y=0, spread=2, block="SAND"),
    S("pose", 3, 34, order="up", stagger=14), S("swap", 46, block="", order="up", stagger=20),
    fx(50, "FALLING_DUST", 60, "ENTITY_HUSK_AMBIENT", 0.5, block="SAND"), S("anim", 68, 30, name="cast")]
DEATH["pharaoh"] = [S("anim", 0, 16, name="die_kneel"), S("flash", 0, 3, block="gold_block"), S("swap", 6, block="sand", order="down", stagger=30),
    fx(8, "FALLING_DUST", 80, "BLOCK_SAND_BREAK", 0.6, block="SAND"), S("drop", 14, 10, tilt=0, rand=0.8, order="down", stagger=40),
    S("scale", 30, 20, s=[1.6, 0.15, 1.6], order="down", stagger=30), fx(40, "FALLING_DUST", 80, "ENTITY_HUSK_DEATH", 0.5, y=0, spread=2, block="SAND"), gone(80, 10)]

SPAWN["executioner"] = [S("shrink", 0, s=0), S("pose", 2, 3, order="up", stagger=50), fx(2, "SMOKE", 20, "BLOCK_NOTE_BLOCK_BASEDRUM", 0.5, y=0),
    fx(18, "SMOKE", 20, "BLOCK_NOTE_BLOCK_BASEDRUM", 0.5, y=0.3), fx(34, "SMOKE", 20, "BLOCK_NOTE_BLOCK_BASEDRUM", 0.5, y=0.6),
    fx(54, "LARGE_SMOKE", 40, "ENTITY_VINDICATOR_CELEBRATE", 0.6), S("anim", 56, 26, name="sweep")]
DEATH["executioner"] = [S("anim", 0, 28, name="die_front"), S("flash", 0, 3, block="red_concrete"), fx(24, "BLOCK", 80, "ENTITY_VINDICATOR_DEATH", 0.6, y=0, spread=2, block="STONE"),
    fx(26, sound="BLOCK_ANVIL_LAND", pitch=0.5), S("move", 40, 30, v=[0, -2.5, 0], order="random", stagger=20),
    fx(46, "LARGE_SMOKE", 40, "BLOCK_GRAVEL_BREAK", 0.6, y=0), gone(76)]

SPAWN["ember_queen"] = [S("scale", 0, s=[0.3, 0.02, 0.3]), fx(0, "LAVA", 40, "BLOCK_LAVA_AMBIENT", 0.6, y=0, spread=1.5, ring=2),
    S("scale", 4, 24, s=[3.3, 50, 3.3]), S("swap", 4, block="magma_block"), fx(14, "FLAME", 120, "ITEM_FIRECHARGE_USE", 0.6, y=0.5, spread=1.4),
    S("swap", 32, block="", order="up", stagger=20), S("light", 34, on=True, only="ring1"), fx(54, "LAVA", 30, "ENTITY_BLAZE_AMBIENT", 0.6, y=0.9), S("anim", 56, 28, name="cast")]
DEATH["ember_queen"] = [S("flash", 0, 3, block="yellow_concrete"), S("anim", 0, 26, name="die_kneel"), fx(0, "FLAME", 60, "ENTITY_BLAZE_DEATH", 0.6),
    S("burst", 10, 16, power=5, up=4, tilt=90, only="ring1"), S("swap", 20, block="basalt", order="up", stagger=24), fx(24, "LARGE_SMOKE", 60, "BLOCK_FIRE_EXTINGUISH", 0.5),
    S("shatter", 48, pieces=3, power=2, up=1, order="down", stagger=16), fx(52, "ASH", 120, "BLOCK_BASALT_BREAK", 0.6, y=0.5, spread=2), gone(72)]

SPAWN["gravelord"] = [S("move", 0, vh=[0, -1.05, 0]), fx(1, "SOUL", 60, "ENTITY_WITHER_SPAWN", 0.6, y=0, spread=2.5, ring=4),
    S("pose", 4, 36, order="up", stagger=24), fx(20, "SOUL_FIRE_FLAME", 40, "BLOCK_SOUL_SAND_BREAK", 0.5, y=0.2),
    fx(44, "SOUL", 80, "ENTITY_WITHER_AMBIENT", 0.6, y=0.6, spread=1.5), S("anim", 46, 30, name="roar")]
DEATH["gravelord"] = [S("anim", 0, 28, name="die_kneel"), S("flash", 0, 3, block="lime_concrete"), fx(0, "SOUL", 40, "ENTITY_WITHER_DEATH", 0.7),
    S("move", 28, 20, v=[0, 4, 0], only="lit"), fx(40, "SOUL_FIRE_FLAME", 80, "ENTITY_WITHER_SKELETON_DEATH", 0.6),
    S("drop", 30, 14, tilt=90, rand=0.6, only="unlit", order="down", stagger=20), S("shrink", 50, 6, s=0, only="lit"),
    fx(56, "SOUL", 100, "BLOCK_SOUL_SAND_BREAK", 0.5, y=0.9, spread=0.6), gone(76, 18)]

SPAWN["captain_brine"] = [S("move", 0, v=[0, 0, -16]), S("tilt", 0, deg=-20, axis="z"), fx(0, "SPLASH", 80, "ENTITY_GENERIC_SPLASH", 0.6, y=0, spread=2),
    S("move", 2, 30, v=[0, 0, 16]), S("tilt", 2, 10, deg=40, axis="z"), S("tilt", 12, 10, deg=-40, axis="z"), S("pose", 22, 10),
    fx(30, sound="BLOCK_BELL_USE", pitch=0.7), fx(32, "SOUL", 30, "ENTITY_DROWNED_AMBIENT", 0.6, y=0.9), S("anim", 34, 28, name="roar")]
DEATH["captain_brine"] = [S("anim", 0, 28, name="die_back"), S("flash", 0, 3, block="lime_concrete"), fx(0, sound="ENTITY_DROWNED_DEATH", pitch=0.6),
    S("fling", 10, power=3, up=4, tilt=300, only="head"), fx(16, "SOUL", 60, "ENTITY_VEX_DEATH", 0.6, y=0.8),
    S("move", 30, 40, v=[0, -4, 0], only="!head"), fx(34, "SPLASH", 120, "ENTITY_GENERIC_SPLASH", 0.5, y=0, spread=2.5), gone(72, 8)]

SPAWN["keywarden"] = [S("shrink", 0, s=0), S("pose", 0, 3, order="up", stagger=30), fx(0, sound="BLOCK_IRON_TRAPDOOR_OPEN", pitch=0.5),
    fx(10, sound="BLOCK_IRON_TRAPDOOR_CLOSE", pitch=0.6), fx(20, sound="BLOCK_IRON_TRAPDOOR_OPEN", pitch=0.7),
    S("spin", 34, 20, deg=360, only="key"), fx(34, "CRIT", 40, "BLOCK_CHAIN_PLACE", 0.6), fx(54, "CAMPFIRE_COSY_SMOKE", 30, "BLOCK_PISTON_EXTEND", 0.5, y=1.0),
    S("anim", 56, 28, name="stomp")]
DEATH["keywarden"] = [S("flash", 0, 3, block="gold_block"), S("shake", 0, 30), fx(0, sound="BLOCK_PISTON_CONTRACT", pitch=0.5),
    S("spin", 10, 30, deg=-720, only="key"), fx(20, "CAMPFIRE_COSY_SMOKE", 40, "ENTITY_IRON_GOLEM_DAMAGE", 0.6, y=1.0),
    S("anim", 30, 28, name="die_front"), S("burst", 54, 14, power=4, up=4, tilt=360, only="copper_block"), fx(54, "EXPLOSION", 2, "BLOCK_CHAIN_BREAK", 0.6),
    S("drop", 60, 12, tilt=90, rand=1, only="!copper_block"), gone(82)]

SPAWN["bloodtusk"] = [S("move", 0, v=[0, 0, -18]), fx(0, "CRIMSON_SPORE", 60, "ENTITY_HOGLIN_ANGRY", 0.6, y=0.2, spread=2), S("move", 2, 16, v=[0, 0, 18]),
    fx(6, "BLOCK", 20, "ENTITY_HOGLIN_STEP", 0.6, y=0, block="NETHERRACK"), fx(12, "BLOCK", 20, "ENTITY_HOGLIN_STEP", 0.6, y=0, block="NETHERRACK"),
    fx(18, "BLOCK", 80, "ENTITY_HOGLIN_ATTACK", 0.5, y=0, spread=2, block="NETHERRACK"), S("anim", 20, 28, name="rear")]
DEATH["bloodtusk"] = [S("anim", 0, 28, name="die_side"), S("flash", 0, 3, block="red_concrete"), fx(0, sound="ENTITY_HOGLIN_DEATH", pitch=0.6),
    S("burst", 20, 10, power=3, up=3, tilt=100, only="iron_block"),
    fx(22, "CRIMSON_SPORE", 80, "BLOCK_NOTE_BLOCK_BASEDRUM", 0.4), S("move", 40, 30, v=[0, -3, 0], order="random", stagger=14), gone(70)]

SPAWN["king_gloop"] = [S("move", 0, v=[0, 30, 0]), S("scale", 0, s=[0.6, 1.6, 0.6]), fx(0, "ITEM_SLIME", 40, "ENTITY_SLIME_JUMP", 0.4, y=2),
    S("move", 2, 16, v=[0, -30, 0]), S("scale", 18, 4, s=[2.6, 0.4, 2.6]), fx(18, "ITEM_SLIME", 160, "ENTITY_SLIME_SQUISH", 0.4, y=0, spread=3, ring=4),
    S("anim", 32, 26, name="burst")]
DEATH["king_gloop"] = [S("flash", 0, 3, block="lime_concrete"), fx(0, sound="ENTITY_SLIME_DEATH", pitch=0.4), S("anim", 0, 30, name="die_deflate"),
    S("fling", 12, power=3, up=5, tilt=360, only="gold_block"), S("drop", 20, 10, tilt=30, only="inner"), fx(24, "ITEM_SLIME", 160, "ENTITY_SLIME_SQUISH", 0.5, y=0.1, spread=3),
    gone(56)]

# ------------------------------------------------------------------------------------------------ seasonal

SPAWN["killer_claus"] = [S("shrink", 0, s=0, only="!sack"), S("move", 0, v=[0, -1.4, 0], only="sack"), fx(0, sound="ENTITY_WITCH_CELEBRATE", pitch=0.5),
    S("shake", 4, 20, only="sack"), fx(10, "SNOWFLAKE", 60, "BLOCK_WOOL_PLACE", 0.6, y=0.3), S("pose", 26, 4, order="up", stagger=24, only="!sack"),
    S("pose", 26, 10, only="sack"), fx(30, "FIREWORK", 40, "ENTITY_FIREWORK_ROCKET_BLAST", 0.8, y=0.8),
    fx(52, sound="ENTITY_WITCH_AMBIENT", pitch=0.4), S("anim", 54, 28, name="roar")]
DEATH["killer_claus"] = [S("anim", 0, 26, name="die_back"), S("flash", 0, 3), fx(0, sound="ENTITY_WITCH_DEATH", pitch=0.5),
    S("fling", 14, power=4, up=6, tilt=360, only="sack"), fx(20, "FIREWORK", 80, "ENTITY_FIREWORK_ROCKET_LARGE_BLAST", 0.8, y=1.2),
    S("fling", 24, power=3, up=3, tilt=200, only="cane"), S("swap", 30, block="snow_block", order="up", stagger=20, only="!sack"),
    fx(36, "SNOWFLAKE", 120, "BLOCK_SNOW_BREAK", 0.6, y=0.4, spread=2), S("drop", 46, 10, tilt=40, rand=1, only="!sack"), gone(72)]

SPAWN["frostbottom"] = [S("shrink", 0, s=0), S("pose", 0, 10, only="core", part=[0, 0.4], order="up"), fx(0, "SNOWFLAKE", 60, "BLOCK_SNOW_PLACE", 0.6, y=0.1, spread=2),
    S("pose", 12, 10, order="up", part=[0.4, 0.75]), fx(12, sound="BLOCK_SNOW_PLACE", pitch=0.8), S("move", 24, v=[0, 8, 0], only="head"),
    S("pose", 24, 12, only="head"), fx(36, sound="ENTITY_SNOW_GOLEM_AMBIENT", pitch=0.5), S("pose", 36, 6, only="arm"), S("pose", 36, 6, only="ring"),
    fx(40, "ITEM_SNOWBALL", 60, "ENTITY_SNOW_GOLEM_SHOOT", 0.6, y=0.7), S("anim", 44, 26, name="spin")]
DEATH["frostbottom"] = [S("flash", 0, 3, block="orange_concrete"), fx(0, sound="ENTITY_SNOW_GOLEM_DEATH", pitch=0.5), S("fling", 4, power=3, up=6, tilt=200, only="head"),
    S("drop", 10, 12, tilt=60, only="arm"), S("scale", 16, 40, s=[1.5, 0.1, 1.5], only="core"), fx(20, "SNOWFLAKE", 80, "BLOCK_SNOW_BREAK", 0.5, y=0.2, spread=2),
    fx(40, "DRIPPING_WATER", 60, "BLOCK_FIRE_EXTINGUISH", 1.4, y=0.1, spread=2), gone(64)]

SPAWN["old_man_winter"] = [S("swap", 0, block="packed_ice"), S("scale", 0, s=[1, 0.02, 1]), fx(0, "SNOWFLAKE", 100, "ENTITY_PLAYER_HURT_FREEZE", 0.5, y=0, spread=3, ring=4),
    S("scale", 4, 30, s=[1, 50, 1]), fx(20, "WHITE_ASH", 120, "BLOCK_POWDER_SNOW_STEP", 0.4, y=0.6, spread=3),
    S("swap", 36, block="", order="down", stagger=24),
    fx(40, "SNOWFLAKE", 80, "BLOCK_GLASS_BREAK", 0.7, y=0.6, spread=2), fx(62, "END_ROD", 30, "ENTITY_ALLAY_AMBIENT_WITHOUT_ITEM", 0.5, y=0.9), S("anim", 64, 30, name="cast")]
DEATH["old_man_winter"] = [S("anim", 0, 30, name="die_kneel"), S("flash", 0, 4, block="light_blue_concrete"), fx(0, "SNOWFLAKE", 80, "ENTITY_STRAY_DEATH", 0.4),
    S("drop", 20, 10, tilt=70, only="staff"), S("swap", 24, block="packed_ice", order="up", stagger=24, only="!staff"), fx(30, "WHITE_ASH", 120, "BLOCK_GLASS_PLACE", 0.5, spread=2),
    S("burst", 54, 18, power=5, up=6, tilt=200, rand=2, order="up", stagger=10, only="!staff"), fx(56, "SNOWFLAKE", 200, "BLOCK_GLASS_BREAK", 0.4, y=0.8, spread=3), gone(80)]

SPAWN["sunscorch"] = [S("move", 0, v=[0, 34, 0]), S("light", 0, on=True), fx(0, "FLAME", 40, "ENTITY_BLAZE_SHOOT", 0.6, y=3),
    S("move", 2, 20, v=[0, -34, 0]), S("scale", 22, 4, s=[1.6, 0.4, 1.6]), fx(22, "LAVA", 80, "ENTITY_GENERIC_SPLASH", 0.6, y=0, spread=3, ring=4),
    S("pose", 26, 10), S("light", 30), fx(36, "FLAME", 40, "ENTITY_MAGMA_CUBE_JUMP", 0.6, y=0.5), S("anim", 38, 24, name="burst")]
DEATH["sunscorch"] = [S("flash", 0, 3, block="yellow_concrete"), fx(0, sound="ENTITY_MAGMA_CUBE_DEATH", pitch=0.5), S("anim", 0, 30, name="die_deflate"),
    S("fling", 10, power=3, up=6, tilt=360, only="white_concrete"), S("swap", 20, block="orange_stained_glass", only="inner"),
    fx(24, "LARGE_SMOKE", 60, "BLOCK_FIRE_EXTINGUISH", 0.6, y=0.3, spread=2), S("scale", 30, 20, s=[1.6, 0.05, 1.6], only="!white_concrete"),
    fx(40, "DRIPPING_HONEY", 60, "BLOCK_HONEY_BLOCK_SLIDE", 0.6, y=0.1, spread=2), gone(64)]

SPAWN["brain_freeze"] = [S("shrink", 0, s=0, only="head"), S("move", 0, v=[0, 16, 0], only="head"), fx(0, "SNOWFLAKE", 40, "BLOCK_HONEY_BLOCK_PLACE", 0.6, y=0.3),
    S("pose", 6, 6, only="head", order="up", part=[0, 0.34]), fx(8, sound="ENTITY_SLIME_SQUISH", pitch=1.2),
    S("pose", 16, 6, only="head", order="up", part=[0.34, 0.68]), fx(18, sound="ENTITY_SLIME_SQUISH", pitch=1.4),
    S("pose", 26, 6, only="head", order="up", part=[0.68, 1]), fx(28, sound="ENTITY_SLIME_SQUISH", pitch=1.6), S("move", 32, 10, v=[0, -16, 0], only="head"),
    fx(42, "SNOWFLAKE", 60, "ENTITY_PLAYER_HURT_FREEZE", 0.6, y=0.9), S("shake", 42, 10, only="head"), S("anim", 50, 26, name="roar")]
DEATH["brain_freeze"] = [S("flash", 0, 3, block="pink_concrete"), fx(0, sound="ENTITY_PLAYER_HURT_FREEZE", pitch=0.5), S("anim", 0, 26, name="die_back"),
    S("fling", 10, power=3, up=6, tilt=200, only="spoon"), S("drop", 20, 14, tilt=20, rand=1, only="head", order="up", stagger=20),
    S("scale", 40, 24, s=[1.6, 0.06, 1.6], only="head"), fx(44, "DRIPPING_HONEY", 80, "BLOCK_HONEY_BLOCK_SLIDE", 0.8, y=0.2, spread=2), gone(72)]

SPAWN["admiral_pinchworth"] = [S("move", 0, vh=[0, -1.0, 0]), fx(0, "FALLING_DUST", 80, "BLOCK_SAND_BREAK", 0.6, y=0, spread=2, block="SAND"),
    S("move", 4, 20, vh=[0, 1.0, 0]), S("pose", 4, 20, only="abdomen"), fx(20, "SPLASH", 60, "ENTITY_GENERIC_SPLASH", 0.6, y=0, spread=2),
    fx(30, sound="BLOCK_NOTE_BLOCK_BELL", pitch=1.2), fx(36, sound="BLOCK_NOTE_BLOCK_BELL", pitch=1.6), S("anim", 30, 24, name="drum")]
DEATH["admiral_pinchworth"] = [S("anim", 0, 32, name="die_curl"), S("flash", 0, 3, block="red_concrete"), fx(0, sound="ENTITY_TURTLE_DEATH", pitch=0.6),
    S("drop", 30, 10, tilt=40, only="abdomen"), S("swap", 32, block="sand", only="abdomen"), S("scale", 40, 20, s=[1.6, 0.1, 1.6], only="abdomen"),
    fx(42, "FALLING_DUST", 80, "BLOCK_SAND_BREAK", 0.6, y=0.1, spread=2, block="SAND"), S("drop", 46, 10, tilt=90, only="!abdomen"), gone(70)]

SPAWN["clucksworth"] = [S("shrink", 0, s=0, only="!shell"), fx(0, sound="ENTITY_CHICKEN_EGG", pitch=0.5), S("shake", 8, 30, only="shell"),
    fx(16, sound="ENTITY_TURTLE_EGG_CRACK", pitch=0.8), fx(30, sound="ENTITY_TURTLE_EGG_CRACK", pitch=0.6),
    S("shatter", 40, pieces=3, power=3, up=3, only="shell"), fx(40, "EGG_CRACK", 60, "ENTITY_TURTLE_EGG_HATCH", 0.6, y=0.4, spread=2), S("pose", 40, 10, only="!shell"),
    fx(54, "CLOUD", 40, "ENTITY_CHICKEN_AMBIENT", 0.4, y=0.8), S("anim", 56, 26, name="roar")]
DEATH["clucksworth"] = [S("flash", 0, 3), fx(0, sound="ENTITY_CHICKEN_DEATH", pitch=0.4), S("anim", 0, 26, name="die_back"),
    S("fling", 20, power=3, up=5, tilt=360, only="pink_concrete"),
    fx(20, "CLOUD", 100, "ENTITY_CHICKEN_HURT", 0.5, y=0.5, spread=2), S("drop", 34, 12, tilt=60, rand=1, only="!pink_concrete"), fx(44, "WHITE_ASH", 60, None, y=0.6, spread=2), gone(64)]

SPAWN["killer_bunny"] = [S("anim", 6, 20, name="stomp"),
    S("scale", 28, 10, s=[4, 4, 4]), fx(28, "DAMAGE_INDICATOR", 30, "ENTITY_RABBIT_ATTACK", 0.4, y=0.6), S("pose", 38, 2), S("light", 38, on=True, only="redstone_block"),
    fx(40, "CHERRY_LEAVES", 60, "ENTITY_RAVAGER_ROAR", 1.8, y=0.6), S("anim", 42, 26, name="slam")]
DEATH["killer_bunny"] = [S("flash", 0, 3, block="red_concrete"), fx(0, sound="ENTITY_RABBIT_DEATH", pitch=0.5), S("anim", 0, 26, name="die_back"),
    S("fling", 10, power=3, up=4, tilt=270, only="carrot"), S("fling", 14, power=2, up=3, tilt=120, only="basket"),
    S("scale", 30, 20, s=[0.25, 0.25, 0.25], only="!carrot"), fx(44, "HEART", 4, "ENTITY_RABBIT_AMBIENT", 1.6, y=0.1), gone(64)]

SPAWN["cocoa_colossus"] = [S("swap", 0, block="gold_block"), S("scale", 0, s=[1, 1, 1]), fx(0, "WAX_ON", 40, "BLOCK_METAL_PLACE", 0.6, y=0.5),
    S("shake", 6, 20), fx(18, sound="BLOCK_COPPER_BREAK", pitch=0.7), S("swap", 26, block="", order="out", stagger=20),
    fx(28, "WAX_ON", 80, "ITEM_ARMOR_EQUIP_GOLD", 0.6, y=0.5, spread=2), S("light", 44, on=True, only="orange_concrete"), S("anim", 48, 28, name="slam")]
DEATH["cocoa_colossus"] = [S("flash", 0, 3, block="orange_concrete"), fx(0, sound="BLOCK_HONEY_BLOCK_BREAK", pitch=0.5), S("anim", 0, 26, name="die_front"),
    S("scale", 24, 30, s=[1.3, 0.3, 1.3], order="up", stagger=10), fx(28, "DRIPPING_HONEY", 80, "BLOCK_HONEY_BLOCK_SLIDE", 0.5, y=0.3, spread=2),
    S("fling", 30, power=3, up=5, tilt=360, only="gold_block"), gone(66)]

SPAWN["great_gourd"] = [S("shrink", 0, s=0, only="!head"), S("move", 0, vh=[0, -0.95, 0], only="head"), fx(0, "BLOCK", 60, "BLOCK_ROOTED_DIRT_BREAK", 0.5, y=0, spread=2, block="DIRT"),
    S("move", 6, 16, vh=[0, 0.95, 0], only="head"), S("light", 22, on=True, only="head"), fx(22, "FLAME", 40, "ITEM_FIRECHARGE_USE", 0.6, y=0.9),
    S("pose", 26, 2, order="down", stagger=24, only="!head"), fx(30, sound="BLOCK_GRASS_PLACE", pitch=0.6), fx(40, sound="ENTITY_WITCH_AMBIENT", pitch=0.6),
    S("anim", 52, 26, name="roar")]
DEATH["great_gourd"] = [S("flash", 0, 3, block="orange_concrete"), fx(0, sound="ENTITY_ZOMBIE_DEATH", pitch=0.5), S("anim", 0, 26, name="die_kneel"),
    S("fling", 10, power=2, up=7, tilt=360, only="crow"), S("drop", 20, 12, tilt=30, rand=0.6, only="head"), S("swap", 24, block="hay_block", order="down", stagger=20, only="!head"),
    S("drop", 30, 14, tilt=90, rand=1.4, only="!head", order="up", stagger=14), fx(34, "BLOCK", 80, "BLOCK_GRASS_BREAK", 0.6, y=0.2, spread=2, block="HAY_BLOCK"),
    S("light", 50, only="head"), fx(52, "SMOKE", 30, "BLOCK_FIRE_EXTINGUISH", 0.6, y=0.1), gone(70)]

SPAWN["headless_horseman"] = [S("move", 0, v=[0, 0, -20]), S("light", 0, on=True), fx(0, "FLAME", 60, "ENTITY_SKELETON_HORSE_AMBIENT", 0.4, y=0.2, spread=1),
    S("move", 2, 24, v=[0, 0, 20]), fx(8, "FLAME", 30, "ENTITY_HORSE_GALLOP", 0.6, y=0), fx(16, "FLAME", 30, "ENTITY_HORSE_GALLOP", 0.6, y=0),
    S("light", 26), S("anim", 26, 30, name="rear"), fx(30, "SOUL_FIRE_FLAME", 60, "ENTITY_WITCH_CELEBRATE", 0.4, y=1.0), fx(34, sound="ENTITY_SKELETON_HORSE_DEATH", pitch=0.6)]
DEATH["headless_horseman"] = [S("anim", 0, 30, name="die_side"), S("flash", 0, 3, block="orange_concrete"), fx(0, sound="ENTITY_SKELETON_HORSE_DEATH", pitch=0.5),
    S("fling", 8, power=4, up=6, tilt=360, only="riderArmL"), fx(14, "FLAME", 60, "ENTITY_WITCH_DEATH", 0.5, y=0.8),
    S("light", 30, only="!riderArmL"), S("swap", 32, block="soul_soil", order="up", stagger=20, only="!riderArmL"),
    fx(40, "SOUL", 80, "BLOCK_SOUL_SAND_BREAK", 0.5, y=0.3, spread=2), S("drop", 50, 10, tilt=40, only="!riderArmL"), gone(76)]

SPAWN["hexmother"] = [S("scale", 0, s=[1, 0.02, 1]), fx(1, "WITCH", 80, "ENTITY_WITCH_CELEBRATE", 0.7, y=0, spread=2, ring=3),
    S("scale", 6, 20, s=[1, 50, 1]), S("pose", 26, 16), fx(26, "WITCH", 50, "ENTITY_ILLUSIONER_CAST_SPELL", 0.8),
    S("move", 30, 12, v=[0, 2, 0], only="hat"), S("move", 42, 10, v=[0, -2, 0], only="hat"), S("anim", 44, 30, name="cast")]
DEATH["hexmother"] = [S("anim", 0, 20, name="die_kneel"), S("flash", 0, 3, block="lime_concrete"), S("swap", 10, block="slime_block", order="down", stagger=20, only="!hat"),
    fx(10, "WITCH", 60, "ENTITY_WITCH_DEATH", 0.8), S("scale", 22, 30, s=[1.8, 0.06, 1.8], only="!hat"), S("drop", 30, 16, tilt=20, only="hat"),
    fx(30, "ITEM_SLIME", 60, "BLOCK_HONEY_BLOCK_SLIDE", 0.6, y=0, spread=2.5), fx(44, "WITCH", 60, "BLOCK_BREWING_STAND_BREW", 0.6, y=0), gone(84, 6)]

# ------------------------------------------------------------------------------------------------ chapters

SPAWN["brakka"] = [S("move", 0, v=[0, 0, -8]), S("pose", 0, 16), fx(0, "CAMPFIRE_COSY_SMOKE", 20, "ENTITY_PILLAGER_AMBIENT", 0.6, y=0.1),
    S("anim", 16, 24, name="double"), fx(24, "CRIT", 30, "ITEM_AXE_STRIP", 0.8, y=0.6), fx(30, sound="ENTITY_PILLAGER_CELEBRATE", pitch=0.7)]
DEATH["brakka"] = [S("anim", 0, 26, name="die_back"), S("flash", 0, 3), fx(0, sound="ENTITY_PILLAGER_DEATH", pitch=0.6),
    S("fling", 10, power=3, up=3, tilt=300, only="axeL"), S("fling", 12, power=3, up=3, tilt=300, only="axeR"),
    S("burst", 30, 10, power=2, up=2, tilt=60, only="gold_block"), S("burst", 30, 10, power=2, up=2, tilt=60, only="emerald_block"),
    fx(32, "HAPPY_VILLAGER", 20, "ENTITY_ITEM_PICKUP", 0.8, y=0.3), gone(56)]

SPAWN["gate_shade"] = [S("shrink", 0, s=0), fx(0, "SQUID_INK", 60, "AMBIENT_CAVE", 0.8, y=0.6, spread=1.5), S("pose", 4, 30, order="down", stagger=20),
    S("light", 0, on=True, only="white_concrete"), fx(30, "SOUL", 40, "BLOCK_CHAIN_PLACE", 0.5, y=0.6), S("anim", 34, 26, name="raise")]
DEATH["gate_shade"] = [S("flash", 0, 3, block="light_blue_concrete"), fx(0, sound="ENTITY_VEX_DEATH", pitch=0.4), S("anim", 0, 26, name="die_drop"),
    S("drop", 16, 10, tilt=40, only="chain"), S("drop", 16, 10, tilt=40, only="iron_block"), S("move", 24, 30, v=[0, 4, 0], only="!chain"),
    S("scale", 24, 30, s=[0.3, 1.6, 0.3], only="!chain"), fx(30, "SQUID_INK", 80, "ENTITY_PHANTOM_DEATH", 0.6, y=0.8, spread=1), gone(54, 6)]

SPAWN["oakheart"] = [S("move", 0, vh=[0, -1.0, 0]), fx(0, "BLOCK", 60, "BLOCK_ROOTED_DIRT_BREAK", 0.5, y=0, spread=2, block="ROOTED_DIRT"),
    S("move", 4, 40, vh=[0, 1.0, 0]), fx(20, "HAPPY_VILLAGER", 40, "BLOCK_WOOD_PLACE", 0.6, y=0.5), S("light", 44, on=True, only="orange_concrete"),
    fx(46, "CHERRY_LEAVES", 40, "BLOCK_AZALEA_LEAVES_BREAK", 0.6, y=1.0), S("anim", 48, 26, name="stomp")]
DEATH["oakheart"] = [S("anim", 0, 26, name="die_front"), S("flash", 0, 3, block="lime_concrete"), fx(0, sound="BLOCK_WOOD_BREAK", pitch=0.5),
    S("drop", 20, 10, tilt=40, rand=1, only="oak_leaves"), S("drop", 20, 10, tilt=40, rand=1, only="azalea_leaves"), S("light", 26, only="orange_concrete"),
    S("swap", 30, block="moss_block", order="down", stagger=20), fx(34, "SPORE_BLOSSOM_AIR", 60, "BLOCK_MOSS_PLACE", 0.6, y=0.2, spread=2), gone(64)]

SPAWN["vault_mimic"] = [S("shrink", 0, s=0, only="leg"), S("tilt", 0, deg=32, axis="x", pivot=[0, 1.0, -0.5], only="head"), fx(0, sound="BLOCK_CHEST_CLOSE", pitch=0.8),
    S("shake", 10, 14), fx(14, sound="BLOCK_CHEST_LOCKED", pitch=0.6), S("pose", 26, 6, only="head"), fx(26, sound="BLOCK_CHEST_OPEN", pitch=0.5),
    S("pose", 30, 10, only="leg", order="random", stagger=8), fx(32, "WAX_ON", 30, "ENTITY_SPIDER_AMBIENT", 1.4, y=0.6), S("anim", 40, 24, name="fang")]
DEATH["vault_mimic"] = [S("flash", 0, 3, block="gold_block"), fx(0, sound="BLOCK_CHEST_CLOSE", pitch=0.4), S("anim", 0, 30, name="die_curl"),
    S("burst", 20, 12, power=3, up=5, tilt=360, only="gold_block"), S("burst", 20, 12, power=3, up=5, tilt=360, only="emerald_block"),
    S("burst", 20, 12, power=3, up=5, tilt=360, only="diamond_block"), fx(22, "WAX_ON", 60, "ENTITY_EXPERIENCE_ORB_PICKUP", 0.8, y=0.4, spread=1.5),
    S("drop", 34, 10, tilt=60, only="leg"), gone(60)]

SPAWN["crypt_knight"] = [S("move", 0, v=[0, 0, 0]), S("tilt", 0, deg=-90, axis="x", pivot=[0, 0, -1]), fx(0, "SOUL", 30, "BLOCK_STONE_BUTTON_CLICK_ON", 0.5, y=0),
    S("pose", 4, 30), fx(16, sound="ENTITY_SKELETON_AMBIENT", pitch=0.4), S("light", 34, on=True, only="light_blue_concrete"),
    fx(36, "SOUL", 30, "ITEM_ARMOR_EQUIP_CHAIN", 0.6, y=0.9), S("anim", 40, 26, name="lunge")]
DEATH["crypt_knight"] = [S("flash", 0, 3, block="light_blue_concrete"), S("anim", 0, 26, name="die_kneel"), fx(0, sound="ENTITY_SKELETON_DEATH", pitch=0.4),
    S("drop", 20, 10, tilt=80, only="shield"), S("drop", 22, 10, tilt=60, only="flail"), S("light", 30, only="light_blue_concrete"),
    S("drop", 30, 14, tilt=80, rand=1, order="down", stagger=20, only="!shield"), fx(40, "SOUL", 60, "BLOCK_CHAIN_BREAK", 0.6, y=0.2), gone(68)]

SPAWN["iron_tusk"] = [S("move", 0, v=[0, 0, -16]), fx(0, "CAMPFIRE_COSY_SMOKE", 20, "ENTITY_HOGLIN_ANGRY", 0.7, y=0.3), S("move", 2, 18, v=[0, 0, 16]),
    fx(8, "BLOCK", 20, "ENTITY_HOGLIN_STEP", 0.6, y=0, block="GRAVEL"), fx(16, "BLOCK", 20, "ENTITY_HOGLIN_STEP", 0.6, y=0, block="GRAVEL"),
    fx(20, "CRIT", 40, "BLOCK_ANVIL_LAND", 0.8, y=0.4), S("anim", 22, 28, name="howl")]
DEATH["iron_tusk"] = [S("anim", 0, 30, name="die_side"), S("flash", 0, 3), fx(0, sound="ENTITY_HOGLIN_DEATH", pitch=0.6),
    S("burst", 24, 12, power=3, up=3, tilt=180, only="iron_block"), fx(26, "CRIT", 60, "BLOCK_ANVIL_LAND", 0.6), S("fling", 26, power=2, up=4, only="red_wool"),
    S("move", 40, 24, v=[0, -2, 0], only="!iron_block"), gone(66)]

SPAWN["reef_hulk"] = [S("move", 0, vh=[0, -1.05, 0]), fx(0, "BUBBLE_COLUMN_UP", 80, "ENTITY_DROWNED_AMBIENT_WATER", 0.5, y=0, spread=1.5),
    S("move", 4, 34, vh=[0, 1.05, 0]), fx(22, "SPLASH", 80, "ENTITY_GENERIC_SPLASH", 0.6, y=0, spread=2), S("pose", 38, 4, only="anchor"),
    fx(40, sound="BLOCK_CHAIN_PLACE", pitch=0.5), S("anim", 40, 26, name="slam")]
DEATH["reef_hulk"] = [S("anim", 0, 26, name="die_front"), S("flash", 0, 3, block="cyan_concrete"), fx(0, sound="ENTITY_DROWNED_DEATH", pitch=0.5),
    S("drop", 20, 10, tilt=90, only="anchor"), S("burst", 26, 12, power=2, up=3, tilt=120, only="fire_coral_block"), S("burst", 26, 12, power=2, up=3, tilt=120, only="tube_coral_block"),
    S("move", 34, 30, v=[0, -3, 0], only="!anchor"), fx(36, "BUBBLE_POP", 80, "ENTITY_GENERIC_SPLASH", 0.6, y=0.1, spread=2), gone(66)]

SPAWN["ember_knight"] = [S("shrink", 0, s=0), S("pose", 0, 2, only="sword"), S("move", 0, v=[0, 6, 0], only="sword"), fx(0, "FLAME", 40, "ITEM_FIRECHARGE_USE", 0.8, y=1.2),
    S("move", 4, 6, v=[0, -6, 0], only="sword"), fx(10, "LAVA", 30, "BLOCK_ANVIL_LAND", 0.6, y=0), S("pose", 12, 3, order="up", stagger=24, only="!sword"),
    fx(36, "FLAME", 60, "ENTITY_BLAZE_AMBIENT", 0.6, y=0.8), S("anim", 40, 26, name="sweep")]
DEATH["ember_knight"] = [S("flash", 0, 3, block="yellow_concrete"), S("anim", 0, 26, name="die_kneel"), fx(0, sound="ENTITY_BLAZE_DEATH", pitch=0.6),
    S("drop", 16, 10, tilt=60, only="ring1"), S("swap", 22, block="basalt", only="lit"), fx(24, "LARGE_SMOKE", 60, "BLOCK_FIRE_EXTINGUISH", 0.6, y=0.6),
    S("drop", 34, 14, tilt=90, rand=1, order="down", stagger=20), gone(66)]

SPAWN["choirmaster"] = [S("shrink", 0, s=0), S("pose", 0, 6, only="book"), fx(0, "NOTE", 10, "BLOCK_NOTE_BLOCK_CHIME", 0.5, y=0.6),
    fx(8, "NOTE", 10, "BLOCK_NOTE_BLOCK_CHIME", 0.6, y=0.6), fx(16, "NOTE", 10, "BLOCK_NOTE_BLOCK_CHIME", 0.75, y=0.6),
    S("pose", 20, 2, order="up", stagger=20, only="!book"), fx(42, sound="BLOCK_BELL_USE", pitch=0.6), fx(44, "SOUL", 30, None, y=0.9), S("anim", 44, 28, name="cast")]
DEATH["choirmaster"] = [S("flash", 0, 3, block="light_blue_concrete"), fx(0, sound="BLOCK_BELL_RESONATE", pitch=0.5), S("anim", 0, 26, name="die_kneel"),
    S("drop", 10, 10, tilt=40, only="book"), fx(14, "NOTE", 10, "BLOCK_NOTE_BLOCK_CHIME", 0.5, y=0.5), fx(22, "NOTE", 10, "BLOCK_NOTE_BLOCK_CHIME", 0.6, y=0.4),
    S("drop", 30, 14, tilt=90, rand=1, order="down", stagger=24, only="!book"), fx(34, "SOUL", 60, "ENTITY_SKELETON_DEATH", 0.6, y=0.3), gone(68)]

SPAWN["sculk_herald"] = [S("scale", 0, s=[1.4, 0.02, 1.4]), S("swap", 0, block="sculk"), fx(0, "SCULK_CHARGE_POP", 60, "BLOCK_SCULK_SPREAD", 0.6, y=0, spread=2, ring=3),
    S("scale", 6, 30, s=[0.72, 50, 0.72]), S("swap", 36, block="", order="up", stagger=16), fx(40, "SCULK_SOUL", 40, "BLOCK_SCULK_SHRIEKER_SHRIEK", 0.8, y=0.8),
    S("anim", 44, 26, name="pulse")]
DEATH["sculk_herald"] = [S("flash", 0, 3, block="cyan_concrete"), fx(0, sound="BLOCK_SCULK_SHRIEKER_SHRIEK", pitch=0.5), S("anim", 0, 26, name="die_drop"),
    S("swap", 16, block="sculk", order="down", stagger=20), fx(20, "SCULK_SOUL", 60, "BLOCK_SCULK_CATALYST_BLOOM", 0.6, y=0.5, spread=1.5),
    S("scale", 36, 20, s=[1.8, 0.05, 1.8]), fx(40, "SCULK_CHARGE_POP", 60, "BLOCK_SCULK_BREAK", 0.6, y=0, spread=2), gone(62)]

# ------------------------------------------------------------------------------------------------ legends

SPAWN["the_listener"] = [S("move", 0, vh=[0, -1.05, 0]), fx(0, "SCULK_CHARGE_POP", 80, "ENTITY_WARDEN_EMERGE", 0.8, y=0, spread=3, ring=5),
    S("move", 6, 70, vh=[0, 1.05, 0]), fx(30, "BLOCK", 120, "ENTITY_WARDEN_EMERGE", 0.6, y=0, spread=3, block="SCULK"),
    S("light", 76, on=True, only="heart"), fx(78, "SCULK_SOUL", 60, "ENTITY_WARDEN_HEARTBEAT", 0.8, y=0.6), fx(90, sound="ENTITY_WARDEN_HEARTBEAT", pitch=0.8),
    S("anim", 96, 30, name="roar"), fx(100, "SONIC_BOOM", 1, "ENTITY_WARDEN_ROAR", 0.8, y=0.8)]
DEATH["the_listener"] = [S("flash", 0, 4, block="cyan_concrete"), fx(0, sound="ENTITY_WARDEN_DEATH", pitch=0.6), S("anim", 0, 30, name="die_kneel"),
    fx(10, sound="ENTITY_WARDEN_HEARTBEAT", pitch=0.7), fx(26, sound="ENTITY_WARDEN_HEARTBEAT", pitch=0.5), S("shrink", 40, 10, s=0, only="heart"),
    fx(42, "SONIC_BOOM", 1, "ENTITY_WARDEN_SONIC_BOOM", 0.5, y=0.6), S("swap", 44, block="sculk", order="up", stagger=24),
    S("scale", 70, 30, s=[1.5, 0.04, 1.5]), fx(72, "SCULK_CHARGE_POP", 120, "BLOCK_SCULK_SPREAD", 0.6, y=0, spread=4), gone(100, 10)]

SPAWN["withered_tyrant"] = [S("shrink", 0, s=0), S("pose", 0, 2, only="core", part=[0, 0.3], order="up"), fx(0, "SOUL_FIRE_FLAME", 60, "BLOCK_SOUL_SAND_PLACE", 0.5, y=0.2),
    S("pose", 20, 30, order="up", stagger=20, only="core"), S("pose", 40, 6, only="armL"), fx(40, "SMOKE", 30, "ENTITY_WITHER_AMBIENT", 0.8, y=0.85),
    S("pose", 50, 6, only="armR"), fx(50, "SMOKE", 30, "ENTITY_WITHER_AMBIENT", 0.7, y=0.85), S("pose", 62, 8, only="head"), S("pose", 62, 8, only="ring"),
    fx(70, "EXPLOSION_EMITTER", 1, "ENTITY_WITHER_SPAWN", 0.7, y=0.6), S("anim", 72, 30, name="pulse")]
DEATH["withered_tyrant"] = [S("flash", 0, 4, block="light_blue_concrete"), fx(0, sound="ENTITY_WITHER_DEATH", pitch=0.7), S("anim", 0, 26, name="die_drop"),
    S("burst", 10, 16, power=6, up=3, tilt=200, only="ring1"), S("fling", 30, power=3, up=4, tilt=300, only="armL"), S("fling", 34, power=3, up=4, tilt=300, only="armR"),
    fx(36, "EXPLOSION", 3, "ENTITY_GENERIC_EXPLODE", 0.8), S("shatter", 50, pieces=3, power=3, up=3, only="head"),
    S("drop", 50, 14, tilt=90, rand=1, only="core"), fx(52, "SOUL", 160, "ENTITY_WITHER_BREAK_BLOCK", 0.6, spread=3), gone(80)]

SPAWN["ender_wyrm"] = [S("move", 0, v=[0, 30, -30]), S("pose", 0, 40), fx(0, "DRAGON_BREATH", 60, "ENTITY_ENDER_DRAGON_FLAP", 0.6, y=0.6, spread=3),
    fx(14, sound="ENTITY_ENDER_DRAGON_FLAP", pitch=0.7), fx(28, sound="ENTITY_ENDER_DRAGON_FLAP", pitch=0.8),
    fx(40, "EXPLOSION_EMITTER", 1, "ENTITY_ENDER_DRAGON_GROWL", 0.8, y=0, ring=6), S("anim", 42, 30, name="howl"),
    fx(50, "DRAGON_BREATH", 120, None, y=0.4, spread=3)]
DEATH["ender_wyrm"] = [S("flash", 0, 4, block="magenta_concrete"), fx(0, sound="ENTITY_ENDER_DRAGON_DEATH", pitch=1.0), S("anim", 0, 30, name="die_collapse"),
    S("light", 10, on=True), S("shake", 10, 50), fx(20, "END_ROD", 100, None, y=0.5, spread=2), fx(40, "END_ROD", 160, None, y=0.5, spread=3),
    S("move", 60, 40, v=[0, 8, 0], order="random", stagger=30), S("shrink", 70, 30, s=0, order="random", stagger=30),
    fx(70, "EXPLOSION_EMITTER", 2, "ENTITY_GENERIC_EXPLODE", 0.5, y=0.5)]

SPAWN["gale_sovereign"] = [S("shrink", 0, s=0, only="!ring"), S("scale", 0, s=[3, 0.2, 3], only="ring"), fx(0, "GUST", 6, "ENTITY_BREEZE_INHALE", 0.6, y=0.1, spread=2),
    S("scale", 4, 24, s=[0.33, 5, 0.33], only="ring"), fx(16, "SMALL_GUST", 60, "ENTITY_BREEZE_IDLE_GROUND", 0.6, y=0.3, spread=2),
    S("pose", 28, 3, order="up", stagger=20, only="!ring"), fx(40, "GUST_EMITTER_LARGE", 1, "ENTITY_BREEZE_WIND_BURST", 0.6, y=0.5),
    S("anim", 50, 26, name="pulse")]
DEATH["gale_sovereign"] = [S("flash", 0, 3, block="white_concrete"), fx(0, sound="ENTITY_BREEZE_DEATH", pitch=0.5), S("anim", 0, 26, name="die_drop"),
    S("burst", 10, 16, power=8, up=4, tilt=200, only="ring"), fx(10, "GUST_EMITTER_LARGE", 1, "ENTITY_BREEZE_WIND_BURST", 0.4, y=0.3),
    S("drop", 26, 12, tilt=120, only="arm"), S("drop", 30, 14, tilt=60, only="head"), S("drop", 34, 14, tilt=40, only="core"),
    fx(40, "SMALL_GUST", 60, "BLOCK_COPPER_BREAK", 0.6, y=0.2, spread=2), gone(64)]

SPAWN["the_unmaker"] = [S("shrink", 0, s=0), S("pose", 0, 30, only="ring3"), fx(0, "REVERSE_PORTAL", 120, "BLOCK_END_PORTAL_SPAWN", 0.5, y=0, spread=4, ring=5),
    S("pose", 30, 10, only="heart"), fx(30, "FLASH", 1, "ENTITY_WARDEN_HEARTBEAT", 0.4, y=0.5), fx(44, sound="ENTITY_WARDEN_HEARTBEAT", pitch=0.4),
    S("pose", 50, 3, order="out", stagger=40, only="!ring3"), fx(56, "PORTAL", 200, "ENTITY_ENDER_DRAGON_GROWL", 0.4, spread=4),
    fx(92, "EXPLOSION_EMITTER", 2, "ENTITY_WITHER_SPAWN", 0.4, y=0.5), S("anim", 94, 40, name="roar")]
DEATH["the_unmaker"] = [S("flash", 0, 4, block="magenta_concrete"), fx(0, sound="ENTITY_ENDER_DRAGON_DEATH", pitch=0.5), S("anim", 0, 44, name="die_drop"),
    S("shake", 0, 60), S("burst", 20, 20, power=10, up=6, tilt=200, only="halo"), S("burst", 20, 20, power=8, up=3, tilt=200, only="ring"),
    fx(40, "FLASH", 1, "ENTITY_GENERIC_EXPLODE", 0.4, y=0.5), S("shatter", 60, pieces=3, power=4, up=4, order="out", stagger=40),
    fx(62, "EXPLOSION_EMITTER", 3, "ENTITY_WITHER_DEATH", 0.6, y=0.5, spread=2), fx(80, "END_ROD", 200, "BLOCK_END_PORTAL_SPAWN", 1.4, y=0.6, spread=4), gone(110, 10)]

# ------------------------------------------------------------------------------------------------ what the viewer says about each

SPAWN_TEXT = {
 "slagheart": "Rises out of a pool of lava, cooling as it climbs, then slams the ground.",
 "warlord_gruk": "A flat pile of gold rises into the warlord, then the gold falls away from feet to helm.",
 "grand_augur": "His gem lights first, he is drawn up out of enchanting runes, and his crown floats down last.",
 "crimson_ronin": "A storm of cherry petals, and the oni assembles piece by piece out of it.",
 "thunderback": "Drops from the sky, craters the ground and roars as lightning hits.",
 "gorehorn": "Charges in from the dark, hoofbeats first, and snorts smoke.",
 "abyssal_eye": "Spins up out of the ground in a column of bubbles, its eye lit.",
 "overgrowth": "Grows out of the ground like a plant, then shakes off its leaves.",
 "prism_sentinel": "Its crystals fly in from every side and lock together, then the core lights.",
 "tiki_warden": "The mask comes down on a drumbeat and the body builds up under it.",
 "hollow_king": "Climbs out of a ring of souls, bones first, then his crown lights.",
 "broodmother": "Lowers herself down on a thread of web.",
 "ironhide_behemoth": "Falls from the sky and shakes the whole arena.",
 "fenrir": "Forms out of a blizzard, tuft by tuft, and howls.",
 "tide_tyrant": "Whirls up out of a whirlpool, spinning, trident first.",
 "void_walker": "Blinks in and out three times around you, then stays.",
 "storm_herald": "Built in three lightning strikes, bottom to top.",
 "pharaoh": "A pillar of sand rises and hardens into the pharaoh, then the sand falls off.",
 "executioner": "Built in the dark to three drumbeats.",
 "ember_queen": "A lava pillar shoots up and cools into the queen, her blaze rods lighting last.",
 "gravelord": "Rises from the grave in a ring of soul fire.",
 "captain_brine": "Sails in on a wave, rocking, and rings the ship's bell.",
 "keywarden": "Assembles to the clank of trapdoors, then its key winds it up.",
 "bloodtusk": "Charges in, every step shaking the netherrack, and rears up.",
 "king_gloop": "Falls from the sky and splats flat, then bounces back into shape.",
 "killer_claus": "His sack drops, shakes, and he climbs out of it laughing.",
 "frostbottom": "Builds himself one snowball at a time; the head goes on last.",
 "old_man_winter": "A pillar of ice grows and shatters to show him inside.",
 "sunscorch": "Cannonballs down from the sky and splashes lava everywhere.",
 "admiral_pinchworth": "Digs up out of the sand and drums his claws.",
 "brain_freeze": "Three scoops land on the cone one at a time, then it gets a brain freeze.",
 "clucksworth": "A painted Easter egg shakes, cracks twice and bursts, and she is inside.",
 "killer_bunny": "A tiny cute bunny hops... then it grows, and its eyes go red.",
 "cocoa_colossus": "A gold-foiled egg shakes and the foil peels away from the inside out.",
 "great_gourd": "The pumpkin head rises out of the patch, lights, then the body grows under it.",
 "headless_horseman": "Gallops in on burning hooves and rears up.",
 "hexmother": "Rises out of a ring of witch smoke and her hat bobs as she cackles.",
 "brakka": "Strides in with his hatchets out.",
 "gate_shade": "Fades in from the top down, eyes first.",
 "oakheart": "Grows up out of the roots and lights his heart.",
 "vault_mimic": "Just a chest... it rattles, opens its lid and stands up on its legs.",
 "crypt_knight": "Rises from lying flat in his tomb to standing.",
 "iron_tusk": "Charges in and screeches to a halt.",
 "reef_hulk": "Rises out of the ground in a column of bubbles and drops his anchor.",
 "ember_knight": "His sword falls first and sticks in the ground, then he builds up beside it.",
 "choirmaster": "His hymn book opens on three notes, then he forms behind it.",
 "sculk_herald": "Sculk spreads across the floor and grows up into the herald.",
 "the_listener": "Digs slowly up out of the ground; its heart beats, then it roars.",
 "withered_tyrant": "Its spine builds up from soul sand, then each head lights in turn.",
 "ender_wyrm": "Flies down out of the sky and lands with a shockwave.",
 "gale_sovereign": "A wind ring spins up into a column and the breeze forms inside it.",
 "the_unmaker": "The rune ring forms, the void heart beats alone, then the titan builds outward from it.",
}

DEATH_TEXT = {
 "slagheart": "The lava inside goes dark, it cools to basalt and breaks apart.",
 "warlord_gruk": "Turns to gold, his maul flies off, and the rest bursts and falls in a heap.",
 "grand_augur": "His crown spins up and fades, the staff flies, the gem shatters, and he melts into the floor.",
 "crimson_ronin": "Kneels, drops the club, and blows away as cherry petals.",
 "thunderback": "Falls back, lightning hits it and it collapses.",
 "gorehorn": "The axe flies, he falls forward and sinks into the ground.",
 "abyssal_eye": "The eye goes grey, the spines fly off and the body drops.",
 "overgrowth": "Turns to dirt from the feet up and crumbles flat.",
 "prism_sentinel": "Trembles and shatters from the core outward.",
 "tiki_warden": "The mask flies off, the flames go out and it falls.",
 "hollow_king": "Drops his sword, the souls leave his body, then the bones fall.",
 "broodmother": "Curls up, her abdomen bursts and the rest collapses.",
 "ironhide_behemoth": "Collapses, its iron plates blow off and it sinks.",
 "fenrir": "Freezes solid from the paws up and shatters.",
 "tide_tyrant": "Drops the trident and spins down into a whirlpool.",
 "void_walker": "Pulled into one point, then bursts into the void.",
 "storm_herald": "Lifted into the sky by lightning and blown apart.",
 "pharaoh": "Turns to sand from the head down and pours into a dune.",
 "executioner": "Falls forward like a felled tree and sinks into the stone.",
 "ember_queen": "Her fire ring flies off, she turns to basalt and crumbles.",
 "gravelord": "The souls rise out of him and fade, the bones drop.",
 "captain_brine": "His head flies off and the body sinks into the sea.",
 "keywarden": "The key spins backwards, steam pours out and the plates blow off.",
 "bloodtusk": "Falls on its side, the armour bursts and it sinks.",
 "king_gloop": "Deflates, his crown pops off and he splats away.",
 "killer_claus": "The sack explodes into fireworks and he turns to snow.",
 "frostbottom": "His head pops off and the rest melts into a puddle.",
 "old_man_winter": "Freezes solid and bursts into a blizzard of ice.",
 "sunscorch": "The beach props fly, it deflates and melts flat.",
 "admiral_pinchworth": "Curls up and crumbles into a sand castle.",
 "brain_freeze": "The spoon flies, the scoops slide off and melt.",
 "clucksworth": "Explodes in a cloud of feathers.",
 "killer_bunny": "Shrinks back to a tiny bunny and hops off as hearts.",
 "cocoa_colossus": "Melts down into chocolate, the foil flying off.",
 "great_gourd": "The crow flies, the body turns to hay and the lantern goes out.",
 "headless_horseman": "The pumpkin flies, the fire goes out and horse and rider turn to soul soil.",
 "hexmother": "Melts into a puddle of slime, leaving her hat.",
 "brakka": "His hatchets fly and his loot spills out.",
 "gate_shade": "The chains drop, the shade stretches upward and fades.",
 "oakheart": "Leaves fall, his heart goes dark and he turns to moss.",
 "vault_mimic": "Spits out its gold, gems and coins, and falls still.",
 "crypt_knight": "Drops his shield and flail and falls apart.",
 "iron_tusk": "Its plates burst off and it sinks.",
 "reef_hulk": "The anchor drops, the coral bursts and he sinks.",
 "ember_knight": "His blaze rods drop, his fire goes out and he falls.",
 "choirmaster": "The book drops, one last note, and he crumbles.",
 "sculk_herald": "Turns to sculk and spreads flat across the floor.",
 "the_listener": "Its heartbeat slows and stops, a last sonic boom, then it turns to sculk.",
 "withered_tyrant": "The orbiting skulls fly, the arms are thrown off and the heads shatter.",
 "ender_wyrm": "Glows from inside like the Ender Dragon and rises away as light.",
 "gale_sovereign": "The wind ring blows apart and the armour falls to the floor.",
 "the_unmaker": "The halo and rings blast away, and the titan shatters from the heart outward.",
}
