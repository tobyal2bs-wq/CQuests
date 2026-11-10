package com.cbosses.fight;

import org.bukkit.Color;
import org.bukkit.Material;
import org.bukkit.Particle;

import java.util.Locale;
import java.util.Map;

/**
 * The look of a boss's effects: its colours, the particles and sounds its attacks use, and the blocks
 * that fly when it hits the ground. Every attack, entrance and death draws from the boss's theme, so a
 * frost boss's shockwave is a ring of ice shards and a fire boss's is a ring of magma, not the same red
 * circle for everyone.
 */
public record Theme(String id, Color main, Color accent, Particle spark, Particle mist, Material debris, Material shard,
                    String charge, String impact, String ambient, String death) {

    private static Theme t(String id, int main, int accent, Particle spark, Particle mist, Material debris, Material shard,
                           String charge, String impact, String ambient, String death) {
        return new Theme(id, Color.fromRGB(main), Color.fromRGB(accent), spark, mist, debris, shard, charge, impact, ambient, death);
    }

    public static final Map<String, Theme> ALL = Map.ofEntries(
            Map.entry("soul", t("soul", 0x7b1fa2, 0x5fe8ff, Particle.SOUL_FIRE_FLAME, Particle.SOUL, Material.SOUL_SOIL, Material.BONE_BLOCK,
                    "ENTITY_WITHER_SKELETON_AMBIENT", "ENTITY_WITHER_BREAK_BLOCK", "PARTICLE_SOUL_ESCAPE", "ENTITY_WITHER_DEATH")),
            Map.entry("fire", t("fire", 0xff6f00, 0xffd54f, Particle.FLAME, Particle.LARGE_SMOKE, Material.MAGMA_BLOCK, Material.BLACKSTONE,
                    "ENTITY_BLAZE_SHOOT", "ENTITY_GENERIC_EXPLODE", "BLOCK_FIRE_AMBIENT", "ENTITY_BLAZE_DEATH")),
            Map.entry("frost", t("frost", 0x4fc3f7, 0xe1f5fe, Particle.SNOWFLAKE, Particle.CLOUD, Material.PACKED_ICE, Material.BLUE_ICE,
                    "ENTITY_PLAYER_HURT_FREEZE", "BLOCK_GLASS_BREAK", "BLOCK_POWDER_SNOW_STEP", "ENTITY_STRAY_DEATH")),
            Map.entry("nature", t("nature", 0x558b2f, 0xaed581, Particle.SPORE_BLOSSOM_AIR, Particle.CHERRY_LEAVES, Material.ROOTED_DIRT, Material.MOSS_BLOCK,
                    "BLOCK_AZALEA_LEAVES_BREAK", "BLOCK_ROOTED_DIRT_BREAK", "BLOCK_GRASS_STEP", "BLOCK_MOSS_BREAK")),
            Map.entry("gold", t("gold", 0xffb300, 0xfff176, Particle.WAX_ON, Particle.CRIT, Material.GOLD_BLOCK, Material.RAW_GOLD_BLOCK,
                    "ENTITY_PIGLIN_BRUTE_ANGRY", "BLOCK_ANVIL_LAND", "BLOCK_CHAIN_STEP", "ENTITY_PIGLIN_BRUTE_DEATH")),
            Map.entry("water", t("water", 0x00838f, 0x80deea, Particle.BUBBLE_POP, Particle.SPLASH, Material.PRISMARINE, Material.DARK_PRISMARINE,
                    "ENTITY_DROWNED_SHOOT", "ENTITY_GENERIC_SPLASH", "BLOCK_BUBBLE_COLUMN_UPWARDS_AMBIENT", "ENTITY_ELDER_GUARDIAN_DEATH")),
            Map.entry("storm", t("storm", 0x3949ab, 0xb3e5fc, Particle.ELECTRIC_SPARK, Particle.CLOUD, Material.LIGHTNING_ROD, Material.COPPER_BLOCK,
                    "ENTITY_EVOKER_PREPARE_ATTACK", "ENTITY_LIGHTNING_BOLT_IMPACT", "WEATHER_RAIN_ABOVE", "ENTITY_LIGHTNING_BOLT_THUNDER")),
            Map.entry("earth", t("earth", 0x6d4c41, 0xbcaaa4, Particle.CAMPFIRE_COSY_SMOKE, Particle.CLOUD, Material.COARSE_DIRT, Material.COBBLESTONE,
                    "ENTITY_RAVAGER_ROAR", "ENTITY_IRON_GOLEM_ATTACK", "BLOCK_GRAVEL_STEP", "ENTITY_RAVAGER_DEATH")),
            Map.entry("blood", t("blood", 0xb71c1c, 0xff8a80, Particle.CRIMSON_SPORE, Particle.DAMAGE_INDICATOR, Material.CRIMSON_NYLIUM, Material.NETHER_WART_BLOCK,
                    "ENTITY_HOGLIN_ANGRY", "ENTITY_HOGLIN_ATTACK", "BLOCK_NETHER_WART_BREAK", "ENTITY_HOGLIN_DEATH")),
            Map.entry("toxic", t("toxic", 0x00e676, 0xccff90, Particle.ITEM_SLIME, Particle.SMOKE, Material.SLIME_BLOCK, Material.GREEN_CONCRETE,
                    "ENTITY_CREEPER_PRIMED", "ENTITY_SLIME_SQUISH", "ENTITY_SLIME_JUMP", "ENTITY_SLIME_DEATH")),
            Map.entry("void", t("void", 0x311b92, 0xb388ff, Particle.REVERSE_PORTAL, Particle.PORTAL, Material.END_STONE, Material.OBSIDIAN,
                    "ENTITY_ENDERMAN_STARE", "ENTITY_ENDERMAN_TELEPORT", "BLOCK_PORTAL_AMBIENT", "ENTITY_ENDER_DRAGON_DEATH")),
            Map.entry("witch", t("witch", 0x8e24aa, 0xce93d8, Particle.WITCH, Particle.ENCHANT, Material.PURPLE_TERRACOTTA, Material.AMETHYST_BLOCK,
                    "ENTITY_EVOKER_PREPARE_SUMMON", "ENTITY_ILLUSIONER_CAST_SPELL", "ENTITY_WITCH_AMBIENT", "ENTITY_WITCH_DEATH")),
            Map.entry("sand", t("sand", 0xfbc02d, 0xfff59d, Particle.WAX_OFF, Particle.FALLING_DUST, Material.SAND, Material.SANDSTONE,
                    "ENTITY_HUSK_AMBIENT", "BLOCK_SAND_BREAK", "BLOCK_SAND_STEP", "ENTITY_HUSK_DEATH")),
            Map.entry("bone", t("bone", 0xd7ccc8, 0xffffff, Particle.WHITE_ASH, Particle.ASH, Material.BONE_BLOCK, Material.CALCITE,
                    "ENTITY_SKELETON_AMBIENT", "BLOCK_BONE_BLOCK_BREAK", "ENTITY_SKELETON_STEP", "ENTITY_SKELETON_DEATH")),
            Map.entry("sculk", t("sculk", 0x0f3b46, 0x29dfeb, Particle.SCULK_SOUL, Particle.SCULK_CHARGE_POP, Material.SCULK, Material.DEEPSLATE,
                    "ENTITY_WARDEN_SONIC_CHARGE", "ENTITY_WARDEN_ATTACK_IMPACT", "ENTITY_WARDEN_HEARTBEAT", "ENTITY_WARDEN_DEATH")),
            Map.entry("wither", t("wither", 0x1c1c1c, 0x9e9e9e, Particle.SMOKE, Particle.LARGE_SMOKE, Material.SOUL_SAND, Material.COAL_BLOCK,
                    "ENTITY_WITHER_SHOOT", "ENTITY_WITHER_BREAK_BLOCK", "ENTITY_WITHER_AMBIENT", "ENTITY_WITHER_DEATH")),
            Map.entry("dragon", t("dragon", 0x6a1b9a, 0xe040fb, Particle.DRAGON_BREATH, Particle.PORTAL, Material.END_STONE_BRICKS, Material.PURPUR_BLOCK,
                    "ENTITY_ENDER_DRAGON_GROWL", "ENTITY_ENDER_DRAGON_SHOOT", "ENTITY_ENDER_DRAGON_FLAP", "ENTITY_ENDER_DRAGON_DEATH")),
            Map.entry("holiday", t("holiday", 0xc62828, 0xffffff, Particle.SNOWFLAKE, Particle.FIREWORK, Material.RED_CONCRETE, Material.SNOW_BLOCK,
                    "BLOCK_NOTE_BLOCK_BELL", "ENTITY_FIREWORK_ROCKET_BLAST", "BLOCK_AMETHYST_BLOCK_CHIME", "ENTITY_FIREWORK_ROCKET_TWINKLE")),
            Map.entry("candy", t("candy", 0xf48fb1, 0xfff3e0, Particle.CHERRY_LEAVES, Particle.CLOUD, Material.PINK_CONCRETE_POWDER, Material.WHITE_CONCRETE,
                    "BLOCK_HONEY_BLOCK_SLIDE", "BLOCK_SLIME_BLOCK_BREAK", "BLOCK_BUBBLE_COLUMN_WHIRLPOOL_INSIDE", "ENTITY_PLAYER_BURP")),
            Map.entry("pumpkin", t("pumpkin", 0xff6d00, 0x7c4dff, Particle.FLAME, Particle.WITCH, Material.PUMPKIN, Material.JACK_O_LANTERN,
                    "ENTITY_WITCH_CELEBRATE", "BLOCK_WOOD_BREAK", "AMBIENT_CAVE", "ENTITY_WITCH_DEATH")),
            Map.entry("feather", t("feather", 0xffffff, 0xffeb3b, Particle.CLOUD, Particle.POOF, Material.HAY_BLOCK, Material.WHITE_WOOL,
                    "ENTITY_CHICKEN_AMBIENT", "ENTITY_CHICKEN_HURT", "ENTITY_CHICKEN_STEP", "ENTITY_CHICKEN_DEATH")),
            Map.entry("wind", t("wind", 0x80cbc4, 0xe0f7fa, Particle.SMALL_GUST, Particle.CLOUD, Material.WAXED_COPPER_BLOCK, Material.WAXED_OXIDIZED_COPPER,
                    "ENTITY_BREEZE_INHALE", "ENTITY_BREEZE_WIND_BURST", "ENTITY_BREEZE_IDLE_AIR", "ENTITY_BREEZE_DEATH")),
            Map.entry("iron", t("iron", 0x455a64, 0x90a4ae, Particle.SMOKE, Particle.CRIT, Material.IRON_BLOCK, Material.POLISHED_DEEPSLATE,
                    "BLOCK_ANVIL_PLACE", "BLOCK_ANVIL_LAND", "BLOCK_CHAIN_STEP", "ENTITY_IRON_GOLEM_DEATH")));

    public static Theme of(String id) {
        Theme t = id == null ? null : ALL.get(id.toLowerCase(Locale.ROOT));
        return t != null ? t : ALL.get("soul");
    }
}
