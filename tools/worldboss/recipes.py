"""How each boss appears and how it dies: timed steps the plugin plays on the model's blocks (and the
preview copies). Every boss has its own pair. Times are ticks (20 a second), distances blocks,
'H' means the model's height. See ModelRig.java for the step reference."""

def S(op, at=0, dur=0, **kw):
    d = {"op": op, "at": at}
    if dur: d["dur"] = dur
    d.update(kw)
    return d

def fx(at, particle=None, count=30, sound=None, pitch=1.0, y=0.5, spread=1.0, **kw):
    d = {"op": "fx", "at": at, "y": y, "spread": spread}
    if particle: d["particle"], d["count"] = particle, count
    if sound: d["sound"], d["pitch"] = sound, pitch
    d.update(kw)
    return d

SPAWN = {
 # gravelord: bones claw up out of the ground in order, soul fire pours from the cracks
 "gravelord": [S("move", 0, vh=[0, -1.05, 0]), fx(1, "SOUL", 60, "ENTITY_WITHER_SPAWN", 0.6, y=0, spread=2.5, ring=4),
               S("pose", 4, 36, order="up", stagger=24), fx(20, "SOUL_FIRE_FLAME", 40, "BLOCK_SOUL_SAND_BREAK", 0.5, y=0.2),
               fx(44, "SOUL", 80, "ENTITY_WITHER_AMBIENT", 0.6, y=0.6, spread=1.5), S("anim", 46, 30, name="roar")],
 # behemoth: thrown down from the sky, lands with a crater shockwave
 "ironhide_behemoth": [S("move", 0, v=[0, 28, 0]), S("pose", 2, 16), fx(18, "EXPLOSION_EMITTER", 2, "ENTITY_GENERIC_EXPLODE", 0.5, y=0, ring=6),
               fx(18, "BLOCK", 120, "ENTITY_RAVAGER_STUNNED", 0.6, y=0, spread=4, block="DIRT"), S("anim", 22, 30, name="howl")],
 # frost jarl: ice shards fly in from all around and lock together
 "frost_jarl": [S("burst", 0, power=9, up=4, tilt=180, rand=3), fx(1, "SNOWFLAKE", 80, "ENTITY_PLAYER_HURT_FREEZE", 0.6, spread=5),
               S("pose", 3, 22, order="random", stagger=26), fx(30, "SNOWFLAKE", 60, "BLOCK_GLASS_PLACE", 0.5, y=0.5, spread=2),
               fx(50, "ITEM_SNOWBALL", 40, "ENTITY_POLAR_BEAR_WARNING", 0.6), S("anim", 50, 28, name="roar")],
 # gruk: a pile of gold that swells and shapes itself into the warlord
 "warlord_gruk": [S("scale", 0, s=[1.5, 0.05, 1.5]), S("swap", 0, block="gold_block"), fx(1, "WAX_ON", 50, "BLOCK_GOLD_BREAK" if False else "BLOCK_METAL_PLACE", 0.6, y=0, spread=2),
               S("pose", 4, 30, order="up", stagger=10), S("swap", 38, block="", order="up", stagger=16),
               fx(40, "WAX_ON", 60, "ENTITY_PIGLIN_BRUTE_ANGRY", 0.7), S("anim", 56, 26, name="stomp")],
 # tide tyrant: rises out of a whirlpool of bubbles, spinning slowly
 "tide_tyrant": [S("move", 0, vh=[0, -1.1, 0]), S("spin", 0, deg=-150), fx(1, "BUBBLE_POP", 80, "ENTITY_ELDER_GUARDIAN_CURSE", 0.7, y=0, spread=3, ring=3),
               S("move", 4, 30, vh=[0, 0.6, 0]), S("spin", 4, 30, deg=75), S("pose", 34, 26), fx(20, "SPLASH", 120, "ENTITY_GENERIC_SPLASH", 0.6, y=0, spread=3),
               fx(60, "BUBBLE_COLUMN_UP", 60, "ENTITY_DROWNED_AMBIENT_WATER", 0.5), S("anim", 60, 28, name="cast")],
 # storm herald: three lightning bolts, each one reveals a third of him
 "storm_herald": [S("shrink", 0, s=0), fx(2, sound="ENTITY_LIGHTNING_BOLT_THUNDER", pitch=1.2, lightning=True),
               S("pose", 4, 4, order="up", part=[0, 0.33]), fx(14, sound="ENTITY_LIGHTNING_BOLT_IMPACT", lightning=True),
               S("pose", 16, 4, order="up", part=[0.33, 0.66]), fx(26, "ELECTRIC_SPARK", 80, "ENTITY_LIGHTNING_BOLT_THUNDER", 0.8, lightning=True),
               S("pose", 28, 4, order="up", part=[0.66, 1]), S("anim", 34, 30, name="cast")],
 # executioner: built from the boots up, block by block, to the sound of a gallows drum
 "executioner": [S("shrink", 0, s=0), S("pose", 2, 3, order="up", stagger=50), fx(2, "SMOKE", 20, "BLOCK_NOTE_BLOCK_BASEDRUM", 0.5, y=0),
               fx(18, "SMOKE", 20, "BLOCK_NOTE_BLOCK_BASEDRUM", 0.5, y=0.3), fx(34, "SMOKE", 20, "BLOCK_NOTE_BLOCK_BASEDRUM", 0.5, y=0.6),
               fx(54, "LARGE_SMOKE", 40, "ENTITY_VINDICATOR_CELEBRATE", 0.6), S("anim", 56, 26, name="sweep")],
 # pharaoh: the sarcophagus sand pours upward into his shape, then the wrappings set
 "pharaoh": [S("swap", 0, block="sand"), S("move", 0, vh=[0, -1.0, 0]), S("scale", 0, s=[0.2, 1, 0.2]),
               fx(1, "FALLING_DUST", 80, "BLOCK_SAND_BREAK", 0.5, y=0, spread=2, block="SAND"),
               S("pose", 3, 34, order="up", stagger=14), S("swap", 46, block="", order="up", stagger=20),
               fx(50, "FALLING_DUST", 60, "ENTITY_HUSK_AMBIENT", 0.5, block="SAND"), S("anim", 68, 30, name="cast")],
 # hexmother: a portal of witch fire flattens open on the floor and she climbs out of it
 "hexmother": [S("scale", 0, s=[1, 0.02, 1]), fx(1, "WITCH", 80, "ENTITY_WITCH_CELEBRATE", 0.7, y=0, spread=2, ring=3),
               S("scale", 6, 20, s=[1, 25, 1]), S("pose", 26, 16), fx(26, "WITCH", 50, "ENTITY_ILLUSIONER_CAST_SPELL", 0.8),
               S("anim", 42, 30, name="cast")],
 # void walker: flickers in and out of four places before arriving
 "void_walker": [S("shrink", 0, s=0), S("pose", 2, 1), S("move", 6, 1, v=[4, 0, 2]), fx(6, "REVERSE_PORTAL", 50, "ENTITY_ENDERMAN_TELEPORT", 0.5),
               S("move", 12, 1, v=[-8, 0, -3]), fx(12, "REVERSE_PORTAL", 50, "ENTITY_ENDERMAN_TELEPORT", 0.7),
               S("move", 18, 1, v=[3, 0, 5]), fx(18, "REVERSE_PORTAL", 50, "ENTITY_ENDERMAN_TELEPORT", 0.9),
               S("pose", 24, 1), fx(24, "PORTAL", 120, "ENTITY_ENDERMAN_SCREAM", 0.6, spread=1.5), S("anim", 26, 28, name="roar")],
 # pale watcher: grows like a tree, trunk first, branches last
 "pale_watcher": [S("scale", 0, s=[0.05, 0.05, 0.05]), fx(1, "SPORE_BLOSSOM_AIR", 40, "BLOCK_CREAKING_HEART_SPAWN", 0.8, y=0),
               S("scale", 4, 24, s=[6, 10, 6]), S("pose", 28, 18, order="out", stagger=20), fx(30, "SPORE_BLOSSOM_AIR", 60, "ENTITY_CREAKING_AMBIENT", 0.6),
               S("anim", 50, 28, name="roar")],
 # molten colossus: lava wells up and cools into plates, top down
 "molten_colossus": [S("swap", 0, block="magma_block"), S("light", 0, on=True), S("shrink", 0, s=0.3), S("move", 0, v=[0, -1, 0]),
               fx(1, "LAVA", 60, "ITEM_BUCKET_EMPTY_LAVA", 0.6, y=0, spread=2), S("pose", 3, 24, order="up", stagger=24),
               S("swap", 34, block="", order="down", stagger=22), S("light", 34, on=False, order="down", stagger=22),
               fx(40, "LARGE_SMOKE", 50, "BLOCK_LAVA_EXTINGUISH", 0.6), S("anim", 60, 26, name="slam")],
 # bloodtusk: charges in from far away
 "bloodtusk": [S("move", 0, v=[0, 0, -18]), S("pose", 2, 16), fx(2, "CRIMSON_SPORE", 40, "ENTITY_HOGLIN_ANGRY", 0.6, y=0.2, spread=2),
               fx(18, "BLOCK", 80, "ENTITY_HOGLIN_ATTACK", 0.6, y=0, spread=3, block="CRIMSON_NYLIUM"), S("anim", 20, 26, name="howl")],
 # ruinmaw: dragged out of the ground by its chains, swaying
 "ruinmaw": [S("move", 0, vh=[0, -1, 0]), S("tilt", 0, axis="x", deg=40), fx(1, "MYCELIUM", 60, "BLOCK_CHAIN_BREAK", 0.6, y=0, spread=2),
               S("move", 4, 20, vh=[0, 0.55, 0]), S("tilt", 4, 20, axis="x", deg=-55), S("pose", 26, 16), fx(26, "MYCELIUM", 60, "ENTITY_ZOGLIN_ANGRY", 0.6),
               S("anim", 44, 30, name="howl")],
 # fenrir: a frost spirit circles twice and becomes the wolf
 "fenrir": [S("shrink", 0, s=0.15), S("move", 0, v=[0, 6, 0]), S("spin", 0, deg=-120), fx(1, "SNOWFLAKE", 60, "ENTITY_WOLF_HOWL", 0.5, y=1.2),
               S("spin", 3, 12, deg=120), S("spin", 15, 12, deg=120), S("pose", 27, 14, order="out", stagger=12), fx(30, "END_ROD", 60, "ENTITY_WOLF_GROWL", 0.5),
               S("anim", 46, 30, name="howl")],
 # volatile colossus: unfolds from a single block of TNT
 "volatile_colossus": [S("toward", 0, y=0.1, k=1), S("shrink", 0, s=0.2), S("swap", 0, block="tnt"), fx(1, "SMOKE", 30, "ENTITY_TNT_PRIMED", 0.6, y=0.1),
               S("pose", 20, 14, order="in", stagger=18), S("swap", 34, block="", order="random", stagger=18), fx(34, "EXPLOSION", 6, "ENTITY_CREEPER_PRIMED", 0.5),
               S("anim", 56, 26, name="rear")],
 # broodmother: lowers itself from above on a thread, then drops the last bit
 "broodmother": [S("move", 0, v=[0, 20, 0]), S("tilt", 0, axis="x", deg=-80), fx(1, "SPORE_BLOSSOM_AIR", 40, "ENTITY_SPIDER_AMBIENT", 0.5, y=2),
               S("move", 3, 30, v=[0, -14, 0]), S("pose", 34, 8), fx(42, "BLOCK", 60, "ENTITY_SPIDER_STEP", 0.5, y=0, spread=3, block="COBWEB"),
               S("anim", 44, 26, name="rearup")],
 # cinder sovereign: a spiral of embers gathers into the rings, the crown lights last
 "cinder_sovereign": [S("toward", 0, y=0.5, k=0.9), S("shrink", 0, s=0.1), S("spin", 0, deg=-140), fx(1, "FLAME", 60, "ENTITY_BLAZE_AMBIENT", 0.6, spread=2),
               S("spin", 3, 12, deg=140), S("pose", 15, 20, order="up", stagger=16), fx(30, "LAVA", 30, "ITEM_FIRECHARGE_USE", 0.6), fx(50, "FLAME", 80, "ENTITY_BLAZE_SHOOT", 0.5, y=0.9),
               S("anim", 52, 26, name="raise")],
 # tempest: a tornado touches down and leaves it behind
 "tempest": [S("burst", 0, power=6, up=10, tilt=0, rand=2), S("spin", 0, deg=140), fx(1, "GUST", 30, "ENTITY_BREEZE_WIND_BURST", 0.5, y=0.3, spread=3),
               S("spin", 3, 10, deg=-140), S("pose", 13, 18, order="down", stagger=12), fx(20, "GUST_EMITTER_SMALL", 6, "ENTITY_BREEZE_IDLE_GROUND", 0.6),
               S("anim", 44, 26, name="spin")],
 # king gloop: four small slimes bounce together and merge
 "king_gloop": [S("move", 0, v=[0, 3, 0], rand=9), S("shrink", 0, s=0.4), fx(1, "ITEM_SLIME", 40, "ENTITY_SLIME_JUMP", 0.8, y=0.2, spread=4),
               S("move", 3, 10, v=[0, 2, 0]), S("pose", 14, 12, order="out", stagger=10), fx(26, "ITEM_SLIME", 80, "ENTITY_SLIME_SQUISH", 0.5, y=0.1, spread=2),
               S("anim", 30, 30, name="slam")],
}

DEATH = {
 "gravelord": [S("anim", 0, 28, name="die_kneel"), fx(0, "SOUL", 40, "ENTITY_WITHER_DEATH", 0.7),
               S("move", 28, 20, v=[0, 4, 0], only="lit"), fx(40, "SOUL_FIRE_FLAME", 80, "ENTITY_WITHER_SKELETON_DEATH", 0.6),
               S("drop", 30, 14, tilt=90, rand=0.6, only="unlit", order="down", stagger=20), S("shrink", 50, 6, s=0, only="lit"),
               fx(56, "SOUL", 100, "BLOCK_SOUL_SAND_BREAK", 0.5, y=0.9, spread=0.6), S("shrink", 76, 18, s=0, order="random", stagger=20)],
 "ironhide_behemoth": [S("anim", 0, 30, name="die_collapse"), fx(14, "BLOCK", 100, "ENTITY_RAVAGER_DEATH", 0.6, y=0, spread=3, block="DIRT"),
               S("burst", 34, 14, power=4, up=2, tilt=120, rand=1, only="polished_deepslate"), fx(34, "EXPLOSION", 4, "BLOCK_ANVIL_LAND", 0.6),
               S("move", 50, 40, v=[0, -3, 0]), fx(60, "CAMPFIRE_COSY_SMOKE", 20, "ENTITY_RAVAGER_STUNNED", 0.5, y=0.2), S("shrink", 80, 10, s=0, order="random", stagger=10)],
 "frost_jarl": [S("anim", 0, 20, name="die_kneel"), S("swap", 6, block="packed_ice", order="up", stagger=14), S("swap", 22, block="ice", order="up", stagger=8),
               fx(20, "SNOWFLAKE", 60, "BLOCK_GLASS_PLACE", 0.5), fx(40, "ITEM_SNOWBALL", 80, "BLOCK_GLASS_BREAK", 0.6),
               S("burst", 40, 10, power=6, up=1, tilt=200, rand=2), S("drop", 50, 8, tilt=60, rand=1), S("shrink", 70, 14, s=0, order="random", stagger=14)],
 "warlord_gruk": [S("anim", 0, 28, name="die_back"), S("swap", 4, block="gold_block", order="down", stagger=20), fx(24, "WAX_ON", 60, "ENTITY_PIGLIN_BRUTE_DEATH", 0.6),
               S("burst", 32, 10, power=2, up=6, tilt=180, rand=1.5), fx(32, "EXPLOSION", 3, "ENTITY_GENERIC_EXPLODE", 1.2),
               S("drop", 42, 12, tilt=90, rand=3), fx(52, "WAX_ON", 60, "BLOCK_CHAIN_PLACE", 0.6, y=0, spread=4), S("shrink", 76, 16, s=0, order="random", stagger=16)],
 "tide_tyrant": [S("anim", 0, 28, name="die_back"), fx(8, "BUBBLE_POP", 60, "ENTITY_DROWNED_DEATH", 0.6, y=0.2, spread=2),
               S("move", 28, 40, v=[0, -5, 0]), fx(30, "BUBBLE_COLUMN_UP", 80, "ENTITY_GENERIC_SPLASH", 0.5, y=0, spread=2.5),
               fx(50, "SPLASH", 120, "BLOCK_BUBBLE_COLUMN_WHIRLPOOL_INSIDE", 0.6, y=0, spread=3), S("shrink", 66, 6, s=0)],
 "storm_herald": [fx(0, sound="ENTITY_LIGHTNING_BOLT_THUNDER", lightning=True), S("move", 0, 20, v=[0, 3, 0]), S("light", 0, on=True),
               fx(10, "ELECTRIC_SPARK", 80, "ENTITY_EVOKER_DEATH", 0.7, lightning=True), S("spin", 20, 10, deg=140), S("move", 20, 10, v=[0, 2, 0]),
               S("spin", 30, 10, deg=140), fx(30, sound="ENTITY_LIGHTNING_BOLT_IMPACT", lightning=True), S("burst", 40, 12, power=5, up=6, tilt=180, rand=2),
               S("shrink", 52, 6, s=0), fx(52, "FIREWORK", 80, "ENTITY_FIREWORK_ROCKET_TWINKLE", 0.8, y=1.2)],
 "executioner": [S("anim", 0, 28, name="die_front"), fx(24, "BLOCK", 80, "ENTITY_VINDICATOR_DEATH", 0.6, y=0, spread=2, block="STONE"),
               fx(26, sound="BLOCK_ANVIL_LAND", pitch=0.5), S("move", 40, 30, v=[0, -2.5, 0], order="random", stagger=20),
               fx(46, "LARGE_SMOKE", 40, "BLOCK_GRAVEL_BREAK", 0.6, y=0), S("shrink", 76, 12, s=0, order="random", stagger=12)],
 "pharaoh": [S("anim", 0, 16, name="die_kneel"), S("swap", 6, block="sand", order="down", stagger=30), fx(8, "FALLING_DUST", 80, "BLOCK_SAND_BREAK", 0.6, block="SAND"),
               S("drop", 14, 10, tilt=0, rand=0.8, order="down", stagger=40), S("scale", 30, 20, s=[1.6, 0.15, 1.6], order="down", stagger=30),
               fx(40, "FALLING_DUST", 80, "ENTITY_HUSK_DEATH", 0.5, y=0, spread=2, block="SAND"), S("shrink", 80, 10, s=0, order="random", stagger=10)],
 "hexmother": [S("anim", 0, 20, name="die_kneel"), S("swap", 10, block="slime_block", order="down", stagger=20), fx(10, "WITCH", 60, "ENTITY_WITCH_DEATH", 0.8),
               S("scale", 22, 30, s=[1.8, 0.06, 1.8]), fx(30, "ITEM_SLIME", 60, "BLOCK_HONEY_BLOCK_SLIDE", 0.6, y=0, spread=2.5),
               fx(44, "EFFECT", 60, "BLOCK_BREWING_STAND_BREW", 0.6, y=0), S("move", 60, 30, v=[0, -0.6, 0]), S("shrink", 88, 4, s=0)],
 "void_walker": [S("toward", 0, 14, y=0.55, k=1), S("spin", 0, 14, deg=150), fx(0, "REVERSE_PORTAL", 80, "ENTITY_ENDERMAN_DEATH", 0.6, y=0.55),
               S("shrink", 14, 6, s=0.1), fx(20, "FLASH", 1, "ENTITY_ENDERMAN_TELEPORT", 0.5, y=0.55, color="#ff40ff"),
               S("burst", 20, 8, power=7, up=0, tilt=200, rand=1), fx(20, "PORTAL", 200, "ENTITY_ENDER_EYE_DEATH", 0.6, y=0.55, spread=2), S("shrink", 28, 4, s=0)],
 "pale_watcher": [S("drop", 0, 16, tilt=60, rand=1, only="pale_oak_log", order="out", stagger=12), fx(0, "CRIMSON_SPORE", 30, "ENTITY_CREAKING_DEATH", 0.7),
               S("anim", 10, 30, name="die_front"), fx(24, "BLOCK", 80, "BLOCK_WOOD_BREAK", 0.6, y=0.2, spread=2, block="PALE_OAK_LOG"),
               S("light", 40, on=False), S("swap", 40, block="black_concrete", only="lit"), fx(44, "SMOKE", 30, "BLOCK_CREAKING_HEART_BREAK", 0.6, y=0.1),
               S("burst", 54, 10, power=2.5, up=0.5, tilt=90, rand=1), S("shrink", 70, 16, s=0, order="random", stagger=16)],
 "molten_colossus": [S("light", 0, on=True), S("swap", 0, block="magma_block", order="random", stagger=20), fx(0, "LAVA", 60, "ENTITY_IRON_GOLEM_DEATH", 0.5),
               S("anim", 16, 26, name="die_kneel"), S("swap", 40, block="obsidian", order="up", stagger=20), S("light", 40, on=False, order="up", stagger=20),
               fx(46, "LARGE_SMOKE", 80, "BLOCK_LAVA_EXTINGUISH", 0.6), S("drop", 64, 12, tilt=40, rand=1.4, order="down", stagger=12),
               fx(70, "BLOCK", 60, "BLOCK_BASALT_BREAK", 0.6, y=0, spread=2.5, block="BLACKSTONE"), S("shrink", 92, 14, s=0, order="random", stagger=14)],
 "bloodtusk": [S("anim", 0, 28, name="die_side"), fx(18, "BLOCK", 60, "ENTITY_HOGLIN_DEATH", 0.6, y=0, spread=2.5, block="CRIMSON_NYLIUM"),
               S("move", 30, 4, v=[0, 0.3, 0]), S("move", 34, 4, v=[0, -0.3, 0]), S("move", 40, 4, v=[0, 0.2, 0]), S("move", 44, 4, v=[0, -0.2, 0]),
               fx(50, "CRIMSON_SPORE", 100, "BLOCK_FUNGUS_BREAK", 0.6, y=0.2, spread=2), S("move", 56, 30, v=[0, -3, 0]), S("shrink", 86, 4, s=0)],
 "ruinmaw": [S("drop", 0, 12, tilt=120, rand=1, only="green_terracotta", order="random", stagger=24), fx(0, "MYCELIUM", 40, "ENTITY_ZOGLIN_DEATH", 0.6),
               S("drop", 12, 12, tilt=120, rand=1, only="lime_terracotta", order="random", stagger=20), fx(20, "SQUID_INK", 30, "ENTITY_SLIME_SQUISH", 0.5, y=0.3),
               S("anim", 30, 26, name="die_collapse"), S("drop", 56, 10, tilt=90, rand=1.5, order="random", stagger=20), fx(60, "BLOCK", 60, "BLOCK_BONE_BLOCK_BREAK", 0.6, y=0, block="BONE_BLOCK"),
               S("shrink", 86, 14, s=0, order="random", stagger=14)],
 "fenrir": [S("anim", 0, 20, name="howl"), fx(0, sound="ENTITY_WOLF_HOWL", pitch=0.5), S("swap", 16, block="light_blue_stained_glass", order="up", stagger=14), S("light", 16, on=True),
               S("move", 30, 30, v=[0, 8, 0]), S("spin", 30, 15, deg=150), S("spin", 45, 15, deg=150), S("shrink", 50, 14, s=0, order="out", stagger=10),
               fx(36, "END_ROD", 80, "BLOCK_AMETHYST_BLOCK_CHIME", 0.6, y=1.2), fx(70, "FIREWORK", 60, "ENTITY_WOLF_HOWL", 1.4, y=2.2)],
 "killer_bunny": [S("scale", 0, 8, s=[1.25, 1.25, 1.25]), fx(0, sound="ENTITY_RABBIT_HURT", pitch=0.5), S("scale", 8, 4, s=[0.9, 0.9, 0.9]),
               S("scale", 12, 6, s=[1.25, 1.25, 1.25]), fx(18, "CLOUD", 120, "ENTITY_CHICKEN_EGG", 0.5, spread=1.5), fx(18, "POOF", 40, "ENTITY_RABBIT_DEATH", 0.6),
               S("burst", 18, 10, power=5, up=4, tilt=200, rand=2), S("drop", 28, 10, tilt=90, rand=3), S("shrink", 40, 10, s=0, order="random", stagger=10),
               fx(40, "HEART", 6, "ENTITY_RABBIT_AMBIENT", 1.6, y=0.2)],
 "volatile_colossus": [S("swap", 0, block="white_concrete"), fx(0, sound="ENTITY_CREEPER_PRIMED", pitch=0.5), S("scale", 0, 6, s=[1.1, 1.1, 1.1]),
               S("swap", 6, block=""), S("scale", 6, 6, s=[0.95, 0.95, 0.95]), S("swap", 12, block="white_concrete"), S("scale", 12, 4, s=[1.2, 1.2, 1.2]),
               S("swap", 16, block=""), S("scale", 16, 4, s=[1.0, 1.0, 1.0]), S("swap", 20, block="white_concrete"), S("scale", 20, 4, s=[1.3, 1.3, 1.3]),
               fx(24, "EXPLOSION_EMITTER", 3, "ENTITY_GENERIC_EXPLODE", 0.6), S("swap", 24, block="tnt"),
               S("burst", 24, 12, power=10, up=6, tilt=240, rand=3), S("drop", 36, 14, tilt=120, rand=4), S("shrink", 60, 14, s=0, order="random", stagger=14)],
 "broodmother": [S("anim", 0, 32, name="die_curl"), fx(0, "SPORE_BLOSSOM_AIR", 40, "ENTITY_SPIDER_DEATH", 0.5), fx(20, "BLOCK", 60, "ENTITY_SPIDER_HURT", 0.5, y=0, block="COBWEB"),
               S("burst", 40, 12, power=4, up=3, tilt=90, rand=1, only="white_wool"), fx(40, "ITEM_SLIME", 30, "ENTITY_TURTLE_EGG_CRACK", 0.6),
               S("move", 56, 30, v=[0, -2, 0]), S("shrink", 84, 12, s=0, order="random", stagger=12)],
 "cinder_sovereign": [S("burst", 0, 14, power=7, up=2, tilt=180, rand=1, only="ring"), fx(0, "LAVA", 40, "ENTITY_BLAZE_DEATH", 0.6),
               S("shrink", 14, 6, s=0, only="ring"), S("anim", 6, 26, name="die_drop"), S("light", 26, on=False, order="up", stagger=20),
               S("swap", 26, block="coal_block", order="up", stagger=20), fx(30, "LARGE_SMOKE", 80, "BLOCK_FIRE_EXTINGUISH", 0.5),
               S("drop", 50, 10, tilt=40, rand=0.8, order="down", stagger=14), fx(56, "ASH", 120, "BLOCK_SAND_BREAK", 0.5, y=0, spread=2), S("shrink", 74, 14, s=0, order="random", stagger=14)],
 "tempest": [S("spin", 0, 10, deg=120), S("spin", 10, 10, deg=120), fx(0, "GUST", 20, "ENTITY_BREEZE_DEATH", 0.6),
               S("burst", 10, 26, power=9, up=7, tilt=0, rand=2, order="down", stagger=16), S("spin", 20, 12, deg=120), S("spin", 32, 12, deg=120),
               fx(14, "GUST_EMITTER_LARGE", 2, "ENTITY_BREEZE_WIND_BURST", 0.5), S("shrink", 40, 10, s=0, order="random", stagger=14),
               fx(50, "CLOUD", 80, "ENTITY_BREEZE_IDLE_AIR", 0.5, y=1.2, spread=4)],
 "king_gloop": [S("anim", 0, 26, name="die_deflate"), fx(0, "ITEM_SLIME", 60, "ENTITY_SLIME_DEATH", 0.5),
               S("drop", 26, 10, tilt=30, rand=1, only="gold_block"), fx(36, sound="BLOCK_CHAIN_FALL", pitch=0.6),
               S("burst", 30, 12, power=6, up=4, tilt=90, rand=2, only="slime_block"), fx(30, "ITEM_SLIME", 100, "ENTITY_SLIME_SQUISH", 0.6, y=0.1, spread=3),
               S("drop", 42, 10, tilt=0, rand=3, only="slime_block"), S("shrink", 70, 16, s=0, order="random", stagger=16), fx(70, sound="ENTITY_SLIME_JUMP_SMALL", pitch=1.2)],
}

# One line each for the preview page.
SPAWN_TEXT = {
 "gravelord": "Claws up out of the ground bone by bone while soul fire pours from the cracks.",
 "ironhide_behemoth": "Dropped from the sky; lands with a crater shockwave and a howl.",
 "frost_jarl": "Ice shards fly in from all around and lock together into the jarl.",
 "warlord_gruk": "A flat pile of gold swells up and hammers itself into the warlord.",
 "tide_tyrant": "Rises slowly out of a whirlpool of bubbles, turning as it comes.",
 "storm_herald": "Three lightning bolts, each one reveals another third of him.",
 "executioner": "Built from the boots up, block by block, to a gallows drum.",
 "pharaoh": "Sand pours upward into his shape, then the wrappings and gold set.",
 "hexmother": "A portal of witch fire opens flat on the floor and she climbs out.",
 "void_walker": "Flickers in and out of three places before it arrives and screams.",
 "pale_watcher": "Grows like a tree: trunk first, branches last.",
 "molten_colossus": "Lava wells up into its shape, then cools into plates from the top down.",
 "bloodtusk": "Charges in from far away and skids to a stop.",
 "ruinmaw": "Dragged out of the ground by its chains, swaying.",
 "fenrir": "A frost spirit circles twice and becomes the wolf.",
 "killer_bunny": "A harmless little rabbit... that keeps growing.",
 "volatile_colossus": "Unfolds out of a single block of TNT.",
 "broodmother": "Lowers itself from above on a thread, then drops the last bit.",
 "cinder_sovereign": "A spiral of embers gathers into the rings; the crown lights last.",
 "tempest": "A tornado touches down and leaves it behind.",
 "king_gloop": "Small slimes bounce together and merge into the king.",
}
DEATH_TEXT = {
 "gravelord": "Sinks to its knees, the soul lantern heart floats up and bursts while the bones rain down.",
 "ironhide_behemoth": "Knees buckle, the armour plates burst off, the carcass sinks into the dirt.",
 "frost_jarl": "Kneels, freezes solid from the feet up, then shatters across the arena.",
 "warlord_gruk": "Falls back, turns to solid gold and bursts into a fountain of gold.",
 "tide_tyrant": "Falls back and sinks into the ground through a column of bubbles.",
 "storm_herald": "Struck by his own lightning, lifted and spun, then blasted apart in fireworks.",
 "executioner": "Falls flat on his face and sinks into the ground in pieces.",
 "pharaoh": "Turns to sand from the crown down and pours into a pile.",
 "hexmother": "Turns to slime and melts into a bubbling puddle.",
 "void_walker": "Pulled into a single point, flashes, and bursts into the void.",
 "pale_watcher": "Branches snap and fall, the trunk topples, the heart goes dark.",
 "molten_colossus": "Glows white hot, cools to obsidian from the feet up, then cracks into rubble.",
 "bloodtusk": "Rolls onto its side, twitches twice, and sinks.",
 "ruinmaw": "The rotten flesh falls off first, then the bare bones collapse.",
 "fenrir": "Howls, turns to glowing ice and spirals up into the sky.",
 "killer_bunny": "Puffs up, wobbles, and pops into fluff.",
 "volatile_colossus": "Flashes white three times, swelling, then explodes into TNT blocks.",
 "broodmother": "Curls its legs and flips over; the egg sacs burst.",
 "cinder_sovereign": "The rings fly off, the fire goes out and it crumbles into coal and ash.",
 "tempest": "Spins faster and faster until the wind tears it apart.",
 "king_gloop": "Deflates into a puddle, the crown clatters down, the slime splats outward.",
}

# ---- seasonal bosses: each arrival and exit is a little joke ----
SPAWN.update({
 # pumpkin king: his head arrives first, bouncing in on its own, then the body rides up out of the flames to catch it
 "headless_horseman": [S("shrink", 0, s=0), S("move", 0, v=[0, 9, 4], only="jack_o_lantern"), S("pose", 2, 12, only="jack_o_lantern"),
               fx(14, "FLAME", 30, "BLOCK_WOOD_PLACE", 0.6, y=0.1), fx(18, sound="ENTITY_WITCH_CELEBRATE", pitch=0.6),
               fx(20, "FLAME", 90, "ENTITY_BLAZE_SHOOT", 0.5, y=0, spread=3, ring=4), S("pose", 20, 22, order="up", stagger=22),
               fx(44, "SOUL_FIRE_FLAME", 60, "ENTITY_SKELETON_HORSE_AMBIENT", 0.5, y=0.7), S("anim", 46, 30, name="rear")],
 # great gourd: a seed in the dirt sprouts, swells in three gulps, and pops its lid to say hello
 "great_gourd": [S("scale", 0, s=[0.08, 0.08, 0.08]), fx(1, "HAPPY_VILLAGER", 20, "ITEM_BONE_MEAL_USE", 0.8, y=0, spread=1),
               S("scale", 8, 6, s=[0.35, 0.35, 0.35]), fx(8, "HAPPY_VILLAGER", 20, "ITEM_BONE_MEAL_USE", 0.9, y=0.1),
               S("scale", 18, 6, s=[0.7, 0.7, 0.7]), fx(18, "HAPPY_VILLAGER", 30, "ITEM_BONE_MEAL_USE", 1.0, y=0.2),
               S("scale", 28, 8, s=[1.15, 0.9, 1.15]), S("scale", 36, 6, s=[1, 1, 1]), fx(30, "BLOCK", 60, "BLOCK_ROOTED_DIRT_BREAK", 0.6, y=0, spread=2.5, block="DIRT"),
               S("anim", 44, 30, name="roar"), fx(48, "WITCH", 50, "ENTITY_WITCH_CELEBRATE", 0.8, y=1)],
 # old man winter: comes down out of the sky very slowly, holding his staff up like an umbrella, grumbling
 "old_man_winter": [S("move", 0, v=[0, 22, 0]), S("spin", 0, deg=-40), fx(1, "SNOWFLAKE", 120, "ENTITY_PLAYER_HURT_FREEZE", 0.5, y=2, spread=4),
               S("move", 2, 44, v=[0, -22, 0]), S("spin", 2, 44, deg=40), fx(24, "SNOWFLAKE", 80, "ENTITY_VILLAGER_NO", 0.6, y=1.4),
               fx(46, "BLOCK", 60, "BLOCK_SNOW_PLACE", 0.6, y=0, spread=2.5, block="SNOW_BLOCK"), S("anim", 48, 30, name="stomp"), fx(60, sound="ENTITY_VILLAGER_NO", pitch=0.5)],
 # frostbottom: three snowballs roll in and stack, the hat flops on last, and it sneezes the carrot nose into place
 "frostbottom": [S("move", 0, v=[0, 0, -10], rand=3), S("spin", 0, deg=-180), S("shrink", 0, s=0.5), fx(1, "ITEM_SNOWBALL", 40, "BLOCK_SNOW_STEP", 0.8, y=0, spread=3),
               S("pose", 2, 26, order="up", stagger=26), fx(10, sound="BLOCK_SNOW_PLACE", pitch=0.7), fx(20, sound="BLOCK_SNOW_PLACE", pitch=0.9),
               fx(32, sound="BLOCK_SNOW_PLACE", pitch=1.1), fx(48, "SNOWFLAKE", 60, "ENTITY_PANDA_SNEEZE", 0.8, y=0.75),
               S("anim", 50, 30, name="roar"), fx(56, sound="ENTITY_SNOW_GOLEM_AMBIENT", pitch=0.5)],
 # killer bunny: a harmless little rabbit... that grows, and grows
 "killer_bunny": [S("scale", 0, s=[0.18, 0.18, 0.18]), fx(1, "HEART", 6, "ENTITY_RABBIT_AMBIENT", 1.2, y=0.1),
               S("scale", 20, 6, s=[0.5, 0.5, 0.5]), fx(20, sound="ENTITY_RABBIT_ATTACK", pitch=0.8), S("scale", 30, 6, s=[1.1, 1.1, 1.1]), fx(30, sound="ENTITY_RABBIT_ATTACK", pitch=0.5),
               fx(38, "ANGRY_VILLAGER", 12, "ENTITY_RAVAGER_ROAR", 1.6, y=0.7), S("scale", 38, 4, s=[1, 1, 1]), S("anim", 44, 26, name="howl")],
 # clucksworth: a giant egg wobbles three times, cracks open, and out comes an extremely angry chicken
 "clucksworth": [S("swap", 0, block="white_concrete"), S("scale", 0, s=[0.75, 0.6, 0.75]), fx(1, "CLOUD", 30, "ENTITY_CHICKEN_EGG", 0.5, y=0.2),
               S("spin", 8, 3, deg=20), S("spin", 11, 3, deg=-40), S("spin", 14, 3, deg=20), fx(10, sound="ENTITY_TURTLE_EGG_CRACK", pitch=0.7),
               S("spin", 22, 3, deg=-25), S("spin", 25, 3, deg=50), S("spin", 28, 3, deg=-25), fx(24, sound="ENTITY_TURTLE_EGG_CRACK", pitch=0.6),
               fx(36, "POOF", 60, "ENTITY_TURTLE_EGG_HATCH", 0.6), S("swap", 36, block="", order="random", stagger=10), S("scale", 36, 8, s=[1, 1, 1]),
               S("anim", 48, 30, name="roar"), fx(50, "CLOUD", 40, "ENTITY_CHICKEN_AMBIENT", 0.5, y=0.8), fx(60, sound="ENTITY_CHICKEN_AMBIENT", pitch=0.6)],
 # sunscorch: falls out of the sky and cannonballs onto its pool float with an enormous splash
 "sunscorch": [S("move", 0, v=[0, 24, 0]), S("light", 0, on=True), fx(1, "FLAME", 40, "ENTITY_BLAZE_SHOOT", 0.6, y=3),
               S("move", 2, 14, v=[0, -24, 0]), S("spin", 2, 14, deg=360), S("scale", 16, 4, s=[1.35, 0.55, 1.35]), S("scale", 20, 6, s=[0.9, 1.2, 0.9]), S("scale", 26, 4, s=[1, 1, 1]),
               fx(16, "SPLASH", 200, "ENTITY_GENERIC_SPLASH", 0.6, y=0.1, spread=4), fx(16, "BUBBLE_POP", 80, "ENTITY_PLAYER_SPLASH_HIGH_SPEED", 0.8, y=0, spread=3, ring=4),
               S("light", 30, on=False, only="unlit"), S("anim", 32, 22, name="burst"), fx(36, sound="ENTITY_DOLPHIN_PLAY", pitch=0.6)],
 # admiral pinchworth: digs up out of the sand sideways, snapping its claws to a drumroll
 "admiral_pinchworth": [S("move", 0, vh=[0, -1.1, 0]), S("move", 0, v=[-6, 0, 0]), fx(1, "BLOCK", 80, "BLOCK_SAND_BREAK", 0.7, y=0, spread=2.5, block="SAND"),
               S("move", 4, 24, vh=[0, 0.6, 0]), S("move", 4, 24, v=[3, 0, 0]), fx(14, "BLOCK", 60, "BLOCK_SAND_BREAK", 0.6, y=0, spread=2, block="SAND"),
               S("pose", 28, 10), fx(38, "SPLASH", 60, "BLOCK_NOTE_BLOCK_HAT", 1.4), fx(42, sound="BLOCK_NOTE_BLOCK_HAT", pitch=1.6),
               S("anim", 40, 30, name="drum"), fx(46, sound="BLOCK_NOTE_BLOCK_HAT", pitch=1.4), fx(64, sound="BLOCK_NOTE_BLOCK_BELL", pitch=0.8)],
})
DEATH.update({
 "headless_horseman": [S("anim", 0, 28, name="rear"), fx(0, sound="ENTITY_SKELETON_HORSE_DEATH", pitch=0.6), S("light", 10, on=True),
               S("swap", 10, block="shroomlight", order="up", stagger=30), fx(16, "FLAME", 100, "ENTITY_BLAZE_SHOOT", 0.5, spread=1.5),
               S("move", 36, 16, v=[0, 9, 0], only="jack_o_lantern"), S("spin", 36, 16, deg=140, only="jack_o_lantern"), fx(52, "EXPLOSION", 3, "ENTITY_WITCH_CELEBRATE", 0.5, y=1.6),
               S("shrink", 52, 2, s=0, only="jack_o_lantern"), fx(52, "FIREWORK", 60, "ENTITY_FIREWORK_ROCKET_BLAST", 0.8, y=1.8),
               S("shrink", 44, 20, s=0, order="up", stagger=30), fx(60, "LARGE_SMOKE", 80, "BLOCK_FIRE_EXTINGUISH", 0.5)],
 # great gourd: the lid blows off, candy fountains out, and the empty pumpkin sags and caves in
 "great_gourd": [S("anim", 0, 24, name="die_back"), fx(0, sound="ENTITY_WITCH_HURT", pitch=0.6),
               S("move", 18, 18, v=[2, 10, 0], only="head"), S("spin", 18, 18, deg=300, only="head"), fx(18, "EXPLOSION", 2, "ENTITY_FIREWORK_ROCKET_BLAST", 0.7, y=0.9),
               fx(20, "FIREWORK", 120, "ENTITY_FIREWORK_ROCKET_TWINKLE", 0.8, y=1), S("burst", 20, 12, power=5, up=6, tilt=200, rand=2, only="arm"),
               S("scale", 34, 16, s=[1.3, 0.25, 1.3]), fx(34, "BLOCK", 80, "BLOCK_SLIME_BLOCK_BREAK", 0.6, y=0, spread=2, block="PUMPKIN"),
               S("shrink", 52, 16, s=0, order="random", stagger=16), fx(66, sound="ENTITY_WITCH_CELEBRATE", pitch=1.4)],
 # old man winter: sneezes himself to bits, then melts into a sad puddle with his slippers floating in it
 "old_man_winter": [S("anim", 0, 20, name="die_kneel"), fx(10, "SNOWFLAKE", 60, "ENTITY_PANDA_PRE_SNEEZE", 0.6, y=0.8),
               fx(22, "SNOWFLAKE", 200, "ENTITY_PANDA_SNEEZE", 0.5, y=0.8, spread=3), S("burst", 22, 10, power=4, up=2, tilt=160, rand=1.5, only="head"),
               S("swap", 26, block="light_blue_stained_glass", order="down", stagger=20), S("scale", 30, 30, s=[1.6, 0.06, 1.6]),
               fx(40, "DRIPPING_WATER", 80, "BLOCK_POWDER_SNOW_BREAK", 0.6, y=0.3, spread=2.5), fx(60, "SPLASH", 60, "ENTITY_GENERIC_SPLASH", 0.8, y=0),
               S("shrink", 66, 20, s=0, order="random", stagger=20)],
 # frostbottom: the head pops off and rolls away, then the rest melts
 "frostbottom": [S("anim", 0, 14, name="hurt"), fx(0, sound="ENTITY_SNOW_GOLEM_DEATH", pitch=0.6),
               S("move", 8, 22, v=[5, -5, 3], only="head"), S("spin", 8, 22, deg=360, only="head"), fx(10, "ITEM_SNOWBALL", 30, "BLOCK_SNOW_BREAK", 0.6, y=0.8),
               S("drop", 14, 12, tilt=60, rand=1, only="arm"), S("swap", 28, block="light_blue_stained_glass", order="down", stagger=16),
               S("scale", 34, 26, s=[1.5, 0.08, 1.5]), fx(36, "DRIPPING_WATER", 80, "BLOCK_POWDER_SNOW_BREAK", 0.7, y=0.3, spread=2),
               S("shrink", 62, 16, s=0, order="random", stagger=16), fx(70, "SPLASH", 40, "ENTITY_GENERIC_SPLASH", 1.2, y=0)],
 # clucksworth: explodes into a cloud of feathers, leaving only the eggshell helmet to fall
 "clucksworth": [S("anim", 0, 22, name="die_back"), fx(0, sound="ENTITY_CHICKEN_HURT", pitch=0.5), fx(12, sound="ENTITY_CHICKEN_HURT", pitch=0.7),
               fx(24, "CLOUD", 160, "ENTITY_CHICKEN_DEATH", 0.5, spread=2), fx(24, "POOF", 80, "ENTITY_GENERIC_EXPLODE", 1.6),
               S("burst", 24, 16, power=6, up=5, tilt=220, rand=3, only="white_wool"), S("shrink", 36, 8, s=0, only="white_wool"),
               S("drop", 28, 14, tilt=120, rand=1.5), fx(44, sound="ENTITY_CHICKEN_EGG", pitch=0.5), fx(52, sound="ENTITY_TURTLE_EGG_BREAK", pitch=0.6),
               S("shrink", 60, 14, s=0, order="random", stagger=14)],
 # sunscorch: the float gets a puncture, it zooms round the arena farting air, then pops into a tiny sunset
 "sunscorch": [S("anim", 0, 20, name="die_deflate"), fx(0, sound="ENTITY_PUFFER_FISH_BLOW_OUT", pitch=0.6),
               S("light", 12, on=True), S("move", 18, 10, v=[4, 5, 0]), S("spin", 18, 10, deg=240), S("move", 28, 10, v=[-8, 2, 3]), S("spin", 28, 10, deg=240),
               S("move", 38, 10, v=[4, 3, -6]), S("spin", 38, 10, deg=240), fx(20, "CLOUD", 30, "ENTITY_PUFFER_FISH_BLOW_OUT", 1.2), fx(32, "CLOUD", 30, "ENTITY_PUFFER_FISH_BLOW_OUT", 0.9),
               fx(42, "CLOUD", 30, "ENTITY_PUFFER_FISH_BLOW_OUT", 0.7), S("shrink", 48, 6, s=0), fx(50, "FLASH", 1, "ENTITY_GENERIC_EXPLODE", 1.2, y=1.6, color="#ffcc33"),
               fx(50, "FIREWORK", 80, "ENTITY_FIREWORK_ROCKET_LARGE_BLAST", 0.8, y=1.6)],
 # admiral pinchworth: flips onto its back, legs kicking, the sandcastle collapses on top of it
 "admiral_pinchworth": [S("anim", 0, 30, name="die_curl"), fx(0, sound="ENTITY_TURTLE_DEATH", pitch=0.8),
               S("move", 0, 10, v=[0, 2, 0]), S("tilt", 2, 12, axis="z", deg=180), S("move", 12, 6, v=[0, -2, 0]), fx(18, "BLOCK", 60, "BLOCK_SAND_FALL", 0.6, y=0, block="SAND"),
               S("drop", 24, 14, tilt=90, rand=2, only="abdomen"), fx(30, "BLOCK", 120, "BLOCK_SAND_BREAK", 0.6, y=0.3, spread=2, block="SANDSTONE"),
               S("move", 44, 30, vh=[0, -1, 0]), fx(46, "BUBBLE_POP", 60, "BLOCK_SAND_BREAK", 0.5, y=0, spread=2), S("shrink", 76, 6, s=0)],
})
SPAWN_TEXT.update({
 "headless_horseman": "His pumpkin head bounces in on its own, then the body rides up out of the flames to catch it.",
 "great_gourd": "A seed sprouts, swells in three big gulps, and pops its lid to say hello.",
 "old_man_winter": "Floats down out of the sky very slowly, grumbling the whole way, and stomps the snow flat.",
 "frostbottom": "Three snowballs roll in and stack up, the hat flops on last, and it sneezes.",
 "killer_bunny": "A harmless little rabbit... that grows, and grows, and gets very angry.",
 "clucksworth": "A giant egg wobbles, cracks, and an extremely angry chicken bursts out.",
 "sunscorch": "Falls out of the sky and cannonballs onto its pool float with a huge splash.",
 "admiral_pinchworth": "Digs up out of the sand sideways and snaps its claws to a drumroll.",
})
DEATH_TEXT.update({
 "headless_horseman": "Rears up and burns from the hooves to the collar; the pumpkin flies up and bursts into fireworks.",
 "great_gourd": "The lid blows off, candy fountains out, and the empty pumpkin caves in.",
 "old_man_winter": "Sneezes so hard his head flies off, then melts into a sad little puddle.",
 "frostbottom": "Its head pops off and rolls away, then the rest melts.",
 "killer_bunny": "Puffs up, wobbles, and pops into fluff.",
 "clucksworth": "Explodes into a cloud of feathers; the eggshell helmet is all that falls.",
 "sunscorch": "Gets a puncture, zooms round the arena blowing out air, then pops into a tiny sunset.",
 "admiral_pinchworth": "Flips onto its back with its legs kicking, and the sandcastle collapses on it.",
})
