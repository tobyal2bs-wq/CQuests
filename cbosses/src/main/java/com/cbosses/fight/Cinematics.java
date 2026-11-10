package com.cbosses.fight;

import com.cbosses.T;

import com.cbosses.util.Text;
import net.kyori.adventure.bossbar.BossBar;
import net.kyori.adventure.title.Title;
import org.bukkit.Bukkit;
import org.bukkit.Color;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.Particle;
import org.bukkit.World;
import org.bukkit.entity.Player;
import org.bukkit.plugin.Plugin;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;

/**
 * The parts of an entrance and a death that happen around the model: before a boss appears, the omen
 * (its rune circle closing in, the ground cracking, its theme's own weather) and after, the title card
 * with the boss bar filling up; when it dies, the shockwave, the pillar of light and the loot fountain.
 * The model itself plays its own entrance and death in between (models.json), different for every boss.
 */
final class Cinematics {
    private final Plugin plugin;
    private final BossService service;

    Cinematics(Plugin plugin, BossService service) { this.plugin = plugin; this.service = service; }

    private void later(Location at, long ticks, Runnable run) {
        Bukkit.getRegionScheduler().runDelayed(plugin, at, t -> run.run(), Math.max(1, ticks));
    }

    /** Ticks the omen takes before the boss appears. */
    static final int OMEN = 50;

    /**
     * The omen: a rune circle in the boss's colours closes in while the ground cracks and lifts around it,
     * the theme's weather builds (lightning for storms, a blizzard for frost, sculk pulses for the Warden...),
     * and it ends in a flash and an eruption of the ground as the boss arrives.
     */
    void omen(Location at, BossDef def, Runnable then) {
        Theme th = Theme.of(def.theme());
        World world = at.getWorld();
        Material ground = Fx.ground(at, th);
        if (service.introDarkness()) for (Player p : at.getNearbyPlayers(40)) if (Bukkit.isOwnedByCurrentRegion(p) && Privacy.sees(p, at)) service.effect(p, "darkness", 70, 0);
        Fx.sound(at, "BLOCK_BEACON_ACTIVATE", 2f, 0.5f);
        Fx.sound(at, th.ambient(), 2f, 0.6f);
        int[] step = {0};
        Bukkit.getRegionScheduler().runAtFixedRate(plugin, at, t -> {
            int i = step[0]++;
            int tick = i * 2;
            if (tick >= OMEN) { t.cancel(); arrival(at, def, th); then.run(); return; }
            double p = (double) tick / OMEN;
            double r = 7.5 - p * 4.5;
            // A character's own motif, without a shared rune ring or dirt eruption.
            int variant = Math.floorMod(def.id().hashCode(), 7);
            double spread = 0.6 + variant * 0.16;
            double height = def.flies() ? 1.5 + p * 2 : 0.3 + p * (1 + variant * 0.13);
            if (tick % 4 == 0) Fx.particle(world, th.spark(), at.clone().add(0, height, 0),
                    3 + variant, spread * (1-p), 0.12, spread * (1-p), 0.015, th);
            themed(at, th, tick, p);
            if (tick == 30) Fx.sound(at, "ENTITY_EVOKER_PREPARE_SUMMON", 2f, 0.6f);

        }, 1, 2);
    }

    /** Each theme's own build-up during the omen. */
    private void themed(Location at, Theme th, int tick, double p) {
        World w = at.getWorld();
        switch (th.id()) {
            case "storm" -> { if (tick == 16 || tick == 32 || tick == 44) w.strikeLightningEffect(at.clone().add(Math.cos(tick) * 6, 0, Math.sin(tick) * 6)); }
            case "frost" -> Fx.particle(w, Particle.SNOWFLAKE, at.clone().add(0, 6, 0), 20, 7, 3, 7, 0.02, th);
            case "fire", "pumpkin" -> { if (tick % 8 == 0) for (int k = 0; k < 4; k++) Fx.pillar(at.clone().add(Math.cos(k * 1.57 + p) * 5, 0, Math.sin(k * 1.57 + p) * 5), Particle.FLAME, th, 3 + p * 3, 0.3); }
            case "sculk" -> {
                if (tick % 10 == 0) { Fx.sound(at, "ENTITY_WARDEN_HEARTBEAT", 2f, 1f); }
                Fx.particle(w, Particle.SCULK_SOUL, at.clone().add(0, 0.4, 0), 3, 4, 0.2, 4, 0.03, th);
                if (tick == 36) Fx.sound(at, "BLOCK_SCULK_SHRIEKER_SHRIEK", 2.5f, 0.8f);
            }
            case "void", "dragon" -> {
                Fx.particle(w, Particle.PORTAL, at.clone().add(0, 1.5, 0), 30, 4 * (1 - p), 1.5, 4 * (1 - p), 0.6, th);
                if (tick == 30 && th.id().equals("dragon")) Fx.sound(at, "ENTITY_ENDER_DRAGON_GROWL", 2.5f, 0.7f);
            }
            case "wither" -> { Fx.particle(w, Particle.LARGE_SMOKE, at.clone().add(0, 2, 0), 20, 4, 2, 4, 0.02, th); if (tick == 20) Fx.sound(at, "ENTITY_WITHER_AMBIENT", 2f, 0.6f); }
            case "water" -> { Fx.particle(w, Particle.BUBBLE_COLUMN_UP, at.clone().add(0, 0.2, 0), 20, 4, 0.1, 4, 0.1, th); Fx.particle(w, Particle.SPLASH, at.clone().add(0, 0.2, 0), 20, 5, 0.1, 5, 0.2, th); }
            case "holiday" -> { if (tick % 8 == 0) Fx.sound(at, "BLOCK_NOTE_BLOCK_BELL", 1.6f, 0.5f + (float) p); Fx.particle(w, Particle.SNOWFLAKE, at.clone().add(0, 5, 0), 12, 6, 2, 6, 0.01, th); }
            case "candy" -> { if (tick % 6 == 0) Fx.debris(at.clone().add(Math.cos(tick) * 4, 4, Math.sin(tick) * 4), Material.PINK_CONCRETE, 2, 1, 0.3, 0.2f); }
            case "wind" -> Fx.particle(w, Particle.SMALL_GUST, at.clone().add(0, 1, 0), 6, 5, 1, 5, 0.02, th);
            case "feather" -> Fx.particle(w, Particle.CLOUD, at.clone().add(0, 3, 0), 6, 3, 1, 3, 0.01, th);
            case "sand" -> Fx.particle(w, Particle.FALLING_DUST, at.clone().add(0, 4, 0), 14, 5, 2, 5, 0, th);
            case "soul", "bone" -> Fx.particle(w, Particle.SOUL, at.clone().add(0, 0.4, 0), 4, 4, 0.2, 4, 0.03, th);
            default -> { }
        }
    }

    private void arrival(Location at, BossDef def, Theme th) {
        World w = at.getWorld();
        int variant = Math.floorMod(def.id().hashCode(), 7);
        Fx.particle(w, th.spark(), at.clone().add(0, .8, 0), 14 + variant * 2, .5 + variant * .1, .7, .5 + variant * .1, .025, th);
        Fx.sound(at, th.impact(), 1.2f, .8f + variant * .06f);
    }

    /** After the model's entrance: the title card for everyone near and the boss bar filling up. */
    void titleCard(Fight f) {
        Location at = f.boss.getLocation();
        String sub = f.def.title().isBlank() ? "" : "<gray><italic>" + Text.escape(f.def.title());
        if (f.def.chapterBoss()) sub = T.t("fight.chapter", "<gold>Chapter ") + f.def.chapter() + " boss</gold>" + (sub.isEmpty() ? "" : " <dark_gray>·</dark_gray> " + sub);
        Title title = Title.title(Text.mm(f.def.name()), Text.mm(sub), Title.Times.times(Duration.ofMillis(300), Duration.ofMillis(2600), Duration.ofMillis(900)));
        for (Player p : at.getNearbyPlayers(56)) if (Bukkit.isOwnedByCurrentRegion(p) && Privacy.sees(p, at)) {
            p.showTitle(title);
            p.playSound(p.getLocation(), org.bukkit.Sound.ENTITY_ENDER_DRAGON_GROWL, 0.7f, 0.8f);
        }
        // the bar fills up like a fighting game's
        f.bar.progress(0f);
        for (int i = 1; i <= 10; i++) {
            float prog = i / 10f;
            service.later(f, i * 2L, () -> f.bar.progress(Math.min(prog, (float) Math.max(0, Math.min(1, f.boss.getHealth() / Math.max(1, f.max))))));
        }
        service.later(f, 22, () -> f.introDone = true);

    }

    /** A phase change: the boss roars, the ground erupts around it and every player near is pushed back. */
    void phase(Fight f, int phase) {
        Location at = f.boss.getLocation();
        World w = at.getWorld();
        Theme th = f.theme;
        f.bar.color(phase >= 2 ? BossBar.Color.RED : BossBar.Color.PURPLE);
        Fx.particle(w, Particle.EXPLOSION_EMITTER, at.clone().add(0, 1, 0), 1, 0, 0, 0, 0, th);
        Fx.eruption(at, 9, Fx.ground(at, th), th, 4);
        Fx.debris(at, Fx.ground(at, th), 12, 5, 2.4, 0.5f);
        Fx.sound(at, th.charge(), 2f, 0.6f);
        Fx.sound(at, "ENTITY_ENDER_DRAGON_GROWL", 1.2f, 0.7f);
        String line = phase == 1 ? T.t("fight.is-enraged", "<red><bold>is enraged!") : T.t("fight.is-desperate", "<dark_red><bold>is desperate!");
        for (Player p : at.getNearbyPlayers(48)) if (Bukkit.isOwnedByCurrentRegion(p) && Privacy.sees(p, at)) {
            p.showTitle(Title.title(Text.mm(f.def.name()), Text.mm(line), Title.Times.times(Duration.ofMillis(150), Duration.ofMillis(1600), Duration.ofMillis(500))));
            if (p.getLocation().distanceSquared(at) < 100 && service.mayHurt(f, p)) {
                org.bukkit.util.Vector v = p.getLocation().toVector().subtract(at.toVector()).setY(0);
                if (v.lengthSquared() > 0.01) p.setVelocity(v.normalize().multiply(1.2).setY(0.5));
            }
        }
        if (f.model != null) f.model.attack(f.model.model.anim("roar") != null ? "roar" : f.model.model.melee);
    }

    /**
     * Around the falling model: a shockwave and a ring of flying ground at once, then when the model's own
     * death has played, a pillar of light, fireworks in the boss's colours and a fountain of its loot.
     */
    void deathStart(Fight f, Location at) {
        World w = at.getWorld();
        Theme th = f.theme;
        Fx.sound(at, th.death(), 2f, 0.8f);
        Fx.sound(at, "ENTITY_PLAYER_ATTACK_CRIT", 2f, 0.5f);
        Fx.particle(w, Particle.FLASH, at.clone().add(0, 1.5, 0), 1, 0, 0, 0, 0, th);
        Fx.ring(at, 4, th.main(), 2.2f, 50);
        Fx.eruption(at, 6, Fx.ground(at, th), th, 3);
    }

    void deathEnd(Fight f, Location at) {
        World w = at.getWorld();
        if (w == null) return;
        Theme th = f.theme;
        double h = f.model == null ? 3 : Math.max(3, f.model.model.blocks());
        Fx.particle(w, Particle.FLASH, at.clone().add(0, h / 2, 0), 1, 0, 0, 0, 0, th);
        Fx.particle(w, Particle.TOTEM_OF_UNDYING, at.clone().add(0, 1, 0), 140, 1.5, 1.5, 1.5, 0.6, th);
        Fx.sound(at, "UI_TOAST_CHALLENGE_COMPLETE", 2f, 1f);
        Fx.sound(at, "ENTITY_FIREWORK_ROCKET_LARGE_BLAST", 2f, 0.8f);
        Fx.sound(at, "BLOCK_BEACON_DEACTIVATE", 2f, 0.6f);
        // a beam of light where it fell
        for (int i = 0; i < 6; i++) {
            int k = i;
            later(at, 1 + i * 3L, () -> {
                for (double y = 0; y < 18; y += 0.7) Fx.particle(w, Particle.END_ROD, at.clone().add(0, y, 0), 1, 0.06, 0.1, 0.06, 0, th);
                Fx.ring(at, 1 + k * 1.4, k % 2 == 0 ? th.main() : th.accent(), 2f, 30 + k * 8);
            });
        }
        // fireworks in the boss's colours, without the rocket
        for (int i = 0; i < 4; i++) {
            later(at, 4 + i * 6L, () -> {
                Location burst = at.clone().add(Math.random() * 6 - 3, h + 2 + Math.random() * 4, Math.random() * 6 - 3);
                Fx.dust(burst, Color.WHITE, 1.4f, 20, 1.2);
                Fx.dust(burst, th.main(), 2f, 30, 1.6);
                Fx.dust(burst, th.accent(), 1.6f, 20, 2);
                Fx.particle(w, Particle.FIREWORK, burst, 30, 0.2, 0.2, 0.2, 0.25, th);
                Fx.sound(burst, "ENTITY_FIREWORK_ROCKET_BLAST", 1.6f, 0.9f + (float) Math.random() * 0.3f);
            });
        }
        List<Material> loot = new ArrayList<>();
        for (String line : f.def.rewards().items()) { Material m = Material.matchMaterial(line.trim().split("\\s+")[0]); if (m != null && m.isItem()) loot.add(m); }
        for (String line : f.def.rewards().topItems()) { Material m = Material.matchMaterial(line.trim().split("\\s+")[0]); if (m != null && m.isItem()) loot.add(m); }
        if (loot.isEmpty()) { loot.add(Material.GOLD_NUGGET); loot.add(Material.EMERALD); }
        loot.add(Material.GOLD_NUGGET);
        Fx.fountain(at, loot, 18);
    }
}
