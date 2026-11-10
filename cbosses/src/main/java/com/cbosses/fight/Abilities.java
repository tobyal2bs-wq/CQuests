package com.cbosses.fight;

import com.cbosses.T;

import com.cbosses.util.Text;
import io.papermc.paper.entity.TeleportFlag;
import org.bukkit.Bukkit;
import org.bukkit.Color;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.Particle;
import org.bukkit.World;
import org.bukkit.entity.AbstractArrow;
import org.bukkit.entity.Arrow;
import org.bukkit.entity.Mob;
import org.bukkit.entity.Player;
import org.bukkit.entity.WitherSkull;
import org.bukkit.event.player.PlayerTeleportEvent;
import org.bukkit.util.Vector;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.concurrent.ThreadLocalRandom;

/**
 * Every boss attack. Each one is announced first (the boss winds up, a ring or line on the ground
 * fills up where it will land) and hits a moment later, so players can see it coming and dodge.
 * The look comes from the boss's theme: a frost boss's quake throws ice, a fire boss's throws magma.
 * They only ever hurt players and never touch a block in the world.
 */
final class Abilities {
    static final Set<String> ALL = Set.of("lightning", "shockwave", "minions", "fire_ring", "pull", "leap", "poison", "blink", "frost",
            "volley", "darkness", "levitate", "heal", "quake", "detonate", "roar",
            "charge", "slam", "meteor", "sonic_boom", "skulls", "breath", "spikes", "orbs", "gifts", "sprinkles", "dive", "eggs");

    private final BossService service;

    Abilities(BossService service) { this.service = service; }

    private static final Material[] CONCRETE = {Material.PINK_CONCRETE, Material.LIME_CONCRETE, Material.LIGHT_BLUE_CONCRETE, Material.YELLOW_CONCRETE,
            Material.ORANGE_CONCRETE, Material.MAGENTA_CONCRETE, Material.WHITE_CONCRETE};

    /** Damage of an attack: its base value scaled by the boss's damage setting, the phase it is in and abilities.damage-multiplier. */
    double dmg(Fight f, double base) {
        double scale = Math.max(0.5, Math.min(2.5, f.def.damage() / 11.0));
        return base * scale * (1 + 0.15 * f.phase) * f.power * service.damageMultiplier();
    }

    private void hurt(Fight f, Player p, double base) {
        if (!service.mayHurt(f, p)) return;
        p.damage(dmg(f, base), f.boss);
    }

    private static void knock(Player p, Location from, double power, double up) {
        Vector v = p.getLocation().toVector().subtract(from.toVector()).setY(0);
        if (v.lengthSquared() < 0.01) v = new Vector(ThreadLocalRandom.current().nextDouble() - 0.5, 0, ThreadLocalRandom.current().nextDouble() - 0.5);
        p.setVelocity(v.normalize().multiply(power).setY(up));
    }

    private static Vector flat(Location from, Location to) {
        Vector v = to.toVector().subtract(from.toVector()).setY(0);
        return v.lengthSquared() < 0.01 ? new Vector(1, 0, 0) : v.normalize();
    }

    /** Runs one attack. Works with no targets too (the self-test). */
    void run(Fight f, String asked, List<Player> targets) {
        Mob boss = f.boss;
        Location at = boss.getLocation();
        World world = at.getWorld();
        Theme th = f.theme;
        Player main = boss.getTarget() instanceof Player p && targets.contains(p) ? p : targets.isEmpty() ? null : targets.get(0);
        final String ability = f.def.flies() && (asked.equals("leap") || asked.equals("charge") || asked.equals("slam")) ? "dive" : asked;
        if (f.model != null) f.model.attack(f.model.model.attackFor(ability)); else boss.swingMainHand();
        double big = Math.max(1, f.model == null ? boss.getHeight() / 2 : f.model.model.blocks() / 4);
        switch (ability) {
            case "lightning" -> {
                List<Location> marks = new ArrayList<>();
                for (Player p : targets.subList(0, Math.min(5, targets.size()))) {
                    Location spot = p.getLocation();
                    marks.add(spot);
                    Fx.telegraph(spot, 2, th, 20);
                    Fx.particle(world, Particle.ELECTRIC_SPARK, spot.clone().add(0, 2.5, 0), 25, 0.4, 1.2, 0.4, 0.05, th);
                }
                if (marks.isEmpty()) marks.add(at.clone().add(3, 0, 0));
                Fx.sound(at, "ENTITY_EVOKER_PREPARE_ATTACK", 1.4f, 0.7f);
                Fx.sound(at, "ITEM_TRIDENT_THUNDER", 0.6f, 1.6f);
                service.later(f, 20, () -> {
                    for (Location spot : marks) {
                        world.strikeLightningEffect(spot);
                        Fx.debris(spot, Fx.ground(spot, th), 6, 2, 1.6, 0.35f);
                        Fx.particle(world, Particle.ELECTRIC_SPARK, spot.clone().add(0, 0.5, 0), 40, 1, 0.5, 1, 0.3, th);
                        for (Player p : service.fighters(f)) if (p.getLocation().distanceSquared(spot) <= 6.25) hurt(f, p, 5);
                    }
                });
            }
            case "shockwave" -> {
                double r = 8;
                Fx.telegraph(at, r, th, 16);
                Fx.sound(at, th.charge(), 1.2f, 0.6f);
                service.later(f, 16, () -> {
                    Location here = boss.getLocation();
                    Fx.sound(here, "ENTITY_GENERIC_EXPLODE", 1.2f, 0.6f);
                    Fx.sound(here, th.impact(), 1.4f, 0.7f);
                    Fx.eruption(here, r, Fx.ground(here, th), th, 4);
                    for (int i = 0; i < 24; i++) {
                        double a = Math.PI * 2 * i / 24;
                        for (double rr = 2; rr <= r; rr += 3) Privacy.particle(world, Particle.SWEEP_ATTACK, here.clone().add(Math.cos(a) * rr, 0.4, Math.sin(a) * rr), 1);
                    }
                    for (Player p : service.fighters(f)) if (p.getLocation().distanceSquared(here) <= r * r) { hurt(f, p, 4); knock(p, here, 1.4, 0.6); }
                });
            }
            case "minions" -> {
                Fx.sound(at, "ENTITY_EVOKER_PREPARE_SUMMON", 1.2f, 0.8f);
                Fx.ring(at, 4, th.main(), 1.6f, 30);
                Fx.particle(world, th.mist(), at.clone().add(0, 0.3, 0), 40, 3, 0.2, 3, 0.02, th);
                service.later(f, 12, () -> service.summonMinions(f, Math.max(1, f.def.minions() / 2)));
            }
            case "fire_ring" -> {
                double r = 6.5;
                Fx.telegraph(at, r, th, 16);
                Fx.sound(at, "ENTITY_BLAZE_SHOOT", 1.2f, 0.6f);
                service.later(f, 16, () -> {
                    Location here = boss.getLocation();
                    Fx.sound(here, "ITEM_FIRECHARGE_USE", 1.2f, 0.7f);
                    for (int wave = 0; wave < 3; wave++) {
                        int w = wave;
                        service.later(f, 1 + wave * 3L, () -> {
                            double rr = r * (0.45 + 0.28 * w);
                            for (int i = 0; i < 36; i++) {
                                double a = Math.PI * 2 * i / 36;
                                Location p = here.clone().add(Math.cos(a) * rr, 0.2, Math.sin(a) * rr);
                                Fx.particle(world, Particle.FLAME, p, 2, 0.1, 0.5, 0.1, 0.02, th);
                                if (i % 6 == 0) Fx.particle(world, Particle.LAVA, p, 1, 0, 0, 0, 0, th);
                            }
                        });
                    }
                    for (Player p : service.fighters(f)) if (p.getLocation().distanceSquared(here) <= r * r && service.mayHurt(f, p)) { p.setFireTicks(80); hurt(f, p, 3); }
                });
            }
            case "pull" -> {
                Fx.sound(at, "ENTITY_EVOKER_PREPARE_SUMMON", 1.2f, 0.6f);
                Fx.sound(at, "BLOCK_PORTAL_TRIGGER", 0.5f, 1.6f);
                for (Player p : targets) {
                    if (!service.mayHurt(f, p)) continue;
                    Vector v = at.toVector().subtract(p.getLocation().toVector());
                    if (v.lengthSquared() < 9) continue;
                    p.setVelocity(v.normalize().multiply(1.3).setY(0.35));
                    Fx.beam(p.getLocation().add(0, 1, 0), at.clone().add(0, 1, 0), th.spark(), th, 0.6);
                }
            }
            case "leap", "slam" -> {
                if (main == null) break;
                Location aim = main.getLocation();
                double r = ability.equals("slam") ? 5.5 : 3.2;
                Fx.telegraph(aim, r, th, ability.equals("slam") ? 22 : 12);
                Fx.sound(at, th.charge(), 1.2f, 1.1f);
                service.later(f, ability.equals("slam") ? 8 : 6, () -> {
                    Location here = boss.getLocation();
                    Vector v = aim.toVector().subtract(here.toVector());
                    double dist = Math.sqrt(v.getX() * v.getX() + v.getZ() * v.getZ());
                    double up = ability.equals("slam") ? 1.15 : 0.75;
                    if (dist > 0.5) service.root(boss).setVelocity(v.setY(0).normalize().multiply(Math.min(2.0, 0.35 + dist / 7)).setY(up));
                    Fx.particle(world, Particle.CLOUD, here, 30, 0.8, 0.2, 0.8, 0.06, th);
                    Fx.debris(here, Fx.ground(here, th), 6, 1.5, 1, 0.4f);
                    service.later(f, ability.equals("slam") ? 16 : 12, () -> {
                        Location land = boss.getLocation();
                        Fx.sound(land, "ENTITY_GENERIC_EXPLODE", 1f, ability.equals("slam") ? 0.6f : 1.3f);
                        Fx.sound(land, th.impact(), 1.4f, 0.8f);
                        Fx.particle(world, Particle.EXPLOSION, land, ability.equals("slam") ? 6 : 3, r / 2, 0.1, r / 2, 0, th);
                        Fx.eruption(land, r, Fx.ground(land, th), th, ability.equals("slam") ? 3 : 2);
                        Fx.debris(land, Fx.ground(land, th), ability.equals("slam") ? 14 : 7, r * 0.8, 2.2, 0.45f);
                        for (Player p : service.fighters(f)) if (p.getLocation().distanceSquared(land) <= r * r) {
                            hurt(f, p, ability.equals("slam") ? 7 : 5);
                            if (service.mayHurt(f, p)) knock(p, land, 0.9, ability.equals("slam") ? 0.95 : 0.5);
                        }
                    });
                });
            }
            case "charge" -> {
                if (main == null) break;
                Location from = at.clone();
                Vector dir = flat(from, main.getLocation());
                Location end = from.clone().add(dir.clone().multiply(14));
                Fx.lineTelegraph(from, end, 2.6, th, 18);
                Fx.sound(from, th.charge(), 1.4f, 0.7f);
                Fx.sound(from, "ENTITY_RAVAGER_ROAR", 1f, 0.9f);
                f.busyUntil = System.currentTimeMillis() + 1800;
                service.later(f, 18, () -> {
                    for (int i = 0; i < 6; i++) {
                        int k = i;
                        service.later(f, 1 + i * 2L, () -> {
                            Location here = boss.getLocation();
                            Vector go = dir.clone().multiply(1.25);
                            go.setY(service.root(boss).getVelocity().getY());
                            service.root(boss).setVelocity(go);
                            Fx.particle(world, th.mist(), here.clone().add(0, 0.6, 0), 12, 0.6, 0.4, 0.6, 0.02, th);
                            if (k % 2 == 0) Fx.debris(here, Fx.ground(here, th), 3, 1.6, 0.9, 0.35f);
                            Fx.sound(here, "ENTITY_RAVAGER_STEP", 1.2f, 0.7f);
                            for (Player p : service.fighters(f)) if (p.getLocation().distanceSquared(here) <= 5.5 * big) {
                                hurt(f, p, 6);
                                if (service.mayHurt(f, p)) knock(p, here, 1.5, 0.55);
                            }
                        });
                    }
                });
            }
            case "poison" -> {
                Fx.sound(at, "ENTITY_SPIDER_AMBIENT", 1.2f, 0.5f);
                Fx.sound(at, "BLOCK_BREWING_STAND_BREW", 1f, 0.6f);
                Color green = Color.fromRGB(0x55aa22);
                for (int i = 0; i < 4; i++) {
                    int k = i;
                    service.later(f, 1 + i * 4L, () -> {
                        Location here = boss.getLocation();
                        Fx.ring(here, 2 + k * 2.2, green, 1.7f, 24 + k * 8);
                        Fx.dust(here.clone().add(0, 1, 0), green, 1.4f, 20, 2 + k);
                    });
                }
                for (Player p : targets) if (p.getLocation().distanceSquared(at) <= 100 && service.mayHurt(f, p)) {
                    service.effect(p, "poison", 80, f.phase > 0 ? 1 : 0);
                    Fx.dust(p.getLocation().add(0, 1, 0), green, 1.4f, 20, 0.6);
                }
            }
            case "blink" -> {
                if (main == null) break;
                Vector facing = main.getLocation().getDirection().setY(0);
                if (facing.lengthSquared() < 0.01) facing = new Vector(1, 0, 0);
                Location behind = main.getLocation().clone().subtract(facing.normalize().multiply(2.5));
                behind.setY(main.getLocation().getY());
                behind.setYaw(main.getLocation().getYaw());
                if (f.arena.contains(behind) && Bukkit.isOwnedByCurrentRegion(behind) && behind.getBlock().isPassable() && behind.clone().add(0, 1, 0).getBlock().isPassable()) {
                    Fx.particle(world, Particle.REVERSE_PORTAL, at.clone().add(0, 1, 0), 70, 0.6, 1.2, 0.6, 0.2, th);
                    Fx.particle(world, th.spark(), at.clone().add(0, 1, 0), 30, 0.6, 1.2, 0.6, 0.05, th);
                    service.root(boss).teleportAsync(behind, PlayerTeleportEvent.TeleportCause.PLUGIN, TeleportFlag.EntityState.RETAIN_PASSENGERS);
                    Fx.sound(behind, "ENTITY_ENDERMAN_TELEPORT", 1.2f, 0.6f);
                    Fx.particle(world, Particle.REVERSE_PORTAL, behind.clone().add(0, 1, 0), 70, 0.6, 1.2, 0.6, 0.2, th);
                    service.later(f, 8, () -> { for (Player p : service.fighters(f)) if (p.getLocation().distanceSquared(boss.getLocation()) <= 9) hurt(f, p, 4); });
                }
            }
            case "frost" -> {
                double r = 11;
                Fx.telegraph(at, r, th, 16);
                Fx.sound(at, "BLOCK_POWDER_SNOW_STEP", 1.6f, 0.5f);
                Fx.sound(at, "ENTITY_PLAYER_HURT_FREEZE", 1f, 0.7f);
                service.later(f, 16, () -> {
                    Location here = boss.getLocation();
                    Fx.sound(here, "BLOCK_GLASS_BREAK", 1.2f, 0.5f);
                    Fx.eruption(here, r, Material.PACKED_ICE, th, 3);
                    Fx.particle(world, Particle.SNOWFLAKE, here.clone().add(0, 1, 0), 80, r / 2, 1, r / 2, 0.05, th);
                    for (Player p : service.fighters(f)) if (p.getLocation().distanceSquared(here) <= r * r && service.mayHurt(f, p)) {
                        service.effect(p, "slowness", 80, 2);
                        p.setFreezeTicks(Math.min(p.getMaxFreezeTicks() + 60, 200));
                        hurt(f, p, 2);
                        Fx.spike(p.getLocation(), Material.ICE, 1.6f, 16);
                    }
                });
            }
            case "volley" -> {
                Fx.sound(at, "ITEM_CROSSBOW_LOADING_END", 1.2f, 0.6f);
                List<Player> aimed = new ArrayList<>(targets.subList(0, Math.min(5, targets.size())));
                for (Player p : aimed) Fx.particle(world, Particle.CRIT, p.getLocation().add(0, 2.2, 0), 12, 0.2, 0.1, 0.2, 0, th);
                for (int wave = 0; wave < 2; wave++) {
                    service.later(f, 12 + wave * 8L, () -> {
                        Fx.sound(boss.getLocation(), "ENTITY_SKELETON_SHOOT", 1.2f, 0.6f);
                        for (Player p : aimed) {
                            if (!p.isValid() || !Bukkit.isOwnedByCurrentRegion(p) || !service.mayHurt(f, p)) continue;
                            Location eye = boss.getEyeLocation();
                            Vector dir = p.getEyeLocation().toVector().subtract(eye.toVector());
                            if (dir.lengthSquared() < 0.01) continue;
                            dir.normalize();
                            for (int i = 0; i < 3; i++) {
                                Arrow arrow = boss.launchProjectile(Arrow.class, dir.clone().multiply(1.8).add(new Vector(ThreadLocalRandom.current().nextGaussian() * 0.05, 0.05, ThreadLocalRandom.current().nextGaussian() * 0.05)));
                                arrow.setPickupStatus(AbstractArrow.PickupStatus.DISALLOWED);
                                arrow.setPersistent(false);
                            }
                        }
                    });
                }
            }
            case "darkness" -> {
                Fx.sound(at, "ENTITY_WARDEN_SONIC_CHARGE", 1.2f, 0.8f);
                Fx.particle(world, Particle.LARGE_SMOKE, at.clone().add(0, 1, 0), 80, 3, 1.4, 3, 0.02, th);
                Fx.particle(world, th.mist(), at.clone().add(0, 1, 0), 40, 3, 1.4, 3, 0.02, th);
                for (Player p : targets) if (service.mayHurt(f, p)) service.effect(p, "darkness", 120, 0);
            }
            case "levitate" -> {
                Fx.sound(at, "ENTITY_SHULKER_SHOOT", 1.2f, 0.6f);
                for (Player p : targets) if (p.getLocation().distanceSquared(at) <= 144 && service.mayHurt(f, p)) {
                    Fx.telegraph(p.getLocation(), 1.4, th, 10);
                    service.later(f, 10, () -> {
                        if (!p.isValid() || !Bukkit.isOwnedByCurrentRegion(p)) return;
                        service.effect(p, "levitation", 40, 0);
                        Fx.particle(world, Particle.END_ROD, p.getLocation(), 20, 0.3, 0.1, 0.3, 0.06, th);
                    });
                }
            }
            case "heal" -> {
                if (f.heals < 2 && boss.getHealth() < f.max * 0.35) {
                    f.heals++;
                    boss.setHealth(Math.min(f.max, boss.getHealth() + f.max * 0.12));
                    Fx.particle(world, Particle.CLOUD, at.clone().add(0, boss.getHeight() / 2, 0), 60, 1, 1, 1, 0.1, th);
                    Fx.pillar(at, Particle.HEART, th, 6, 1.2);
                    Fx.sound(at, "BLOCK_BEACON_POWER_SELECT", 1.2f, 0.8f);
                    for (Player p : targets) p.sendActionBar(Text.mm(T.t("fight.heals-itself", "<boss> <green>heals itself!", "boss", f.def.name())));
                } else run(f, "shockwave", targets);
            }
            case "quake" -> {
                double r = 10;
                Fx.telegraph(at, r, th, 16);
                Fx.sound(at, "ENTITY_IRON_GOLEM_ATTACK", 1.2f, 0.4f);
                service.later(f, 16, () -> {
                    Location here = boss.getLocation();
                    Fx.sound(here, "ENTITY_IRON_GOLEM_HURT", 1.2f, 0.4f);
                    Fx.sound(here, "ENTITY_WARDEN_ATTACK_IMPACT", 1f, 0.6f);
                    Fx.eruption(here, r, Fx.ground(here, th), th, 5);
                    for (Player p : service.fighters(f)) if (p.getLocation().distanceSquared(here) <= r * r && p.isOnGround()) {
                        hurt(f, p, 4);
                        if (service.mayHurt(f, p)) { service.effect(p, "slowness", 40, 1); p.setVelocity(new Vector(0, 0.65, 0)); }
                    }
                });
            }
            case "detonate" -> {
                double r = 7;
                Fx.sound(at, "ENTITY_CREEPER_PRIMED", 1.6f, 0.5f);
                Fx.telegraph(at, r, th, 30);
                if (f.model != null) f.model.attack(f.model.model.attackFor("detonate"));
                service.later(f, 30, () -> {
                    Location here = boss.getLocation();
                    Fx.particle(world, Particle.EXPLOSION_EMITTER, here, 1, 0, 0, 0, 0, th);
                    Fx.sound(here, "ENTITY_GENERIC_EXPLODE", 1.6f, 0.8f);
                    Fx.debris(here, Fx.ground(here, th), 16, r, 3, 0.5f);
                    Fx.eruption(here, r, Fx.ground(here, th), th, 3);
                    for (Player p : service.fighters(f)) if (p.getLocation().distanceSquared(here) <= r * r) {
                        hurt(f, p, 7);
                        if (service.mayHurt(f, p)) knock(p, here, 1.6, 0.8);
                    }
                });
            }
            case "meteor" -> {
                List<Location> spots = new ArrayList<>();
                for (Player p : targets.subList(0, Math.min(5, targets.size()))) spots.add(p.getLocation());
                ThreadLocalRandom rnd = ThreadLocalRandom.current();
                while (spots.size() < 3) spots.add(at.clone().add(rnd.nextInt(-8, 9), 0, rnd.nextInt(-8, 9)));
                Fx.sound(at, th.charge(), 1.4f, 0.5f);
                Fx.sound(at, "ENTITY_BLAZE_SHOOT", 1f, 0.5f);
                for (int i = 0; i < spots.size(); i++) {
                    Location spot = spots.get(i);
                    if (!Bukkit.isOwnedByCurrentRegion(spot)) continue;
                    Fx.telegraph(spot, 3, th, 24 + i * 4);
                    service.later(f, 4 + i * 4L, () -> Fx.meteor(spot, th.debris(), th, 20, 1.3f, () -> {
                        Fx.particle(world, Particle.EXPLOSION, spot, 3, 0.8, 0.2, 0.8, 0, th);
                        Fx.sound(spot, "ENTITY_GENERIC_EXPLODE", 1.2f, 0.9f);
                        Fx.sound(spot, th.impact(), 1.2f, 0.8f);
                        Fx.debris(spot, th.debris(), 8, 3, 2.2, 0.4f);
                        for (Player p : service.fighters(f)) if (p.getLocation().distanceSquared(spot) <= 9) { hurt(f, p, 6); if (service.mayHurt(f, p)) knock(p, spot, 0.8, 0.6); }
                    }));
                }
            }
            case "sonic_boom" -> {
                if (main == null) { Fx.sound(at, "ENTITY_WARDEN_SONIC_CHARGE", 1.4f, 1f); break; }
                Player victim = main;
                Fx.sound(at, "ENTITY_WARDEN_SONIC_CHARGE", 2f, 1f);
                f.busyUntil = System.currentTimeMillis() + 1800;
                for (int i = 0; i < 6; i++) {
                    int k = i;
                    service.later(f, 1 + i * 4L, () -> {
                        Location chest = boss.getLocation().add(0, Math.max(1.5, boss.getHeight() * 0.65 * big), 0);
                        for (int j = 0; j < 10; j++) {
                            double a = Math.PI * 2 * j / 10 + k;
                            Location from = chest.clone().add(Math.cos(a) * (3 - k * 0.45), Math.sin(a) * (3 - k * 0.45) * 0.6, Math.sin(a) * 0.5);
                            Fx.particle(world, Particle.SCULK_CHARGE_POP, from, 1, 0, 0, 0, 0, th);
                        }
                        Fx.line(boss.getLocation(), victim.getLocation(), Color.fromRGB(0x29dfeb), 1f, 1.2);
                    });
                }
                service.later(f, 28, () -> {
                    if (!victim.isValid() || !Bukkit.isOwnedByCurrentRegion(victim)) return;
                    Location chest = boss.getLocation().add(0, Math.max(1.5, boss.getHeight() * 0.65 * big), 0);
                    Location end = victim.getEyeLocation().add(victim.getLocation().toVector().subtract(chest.toVector()).normalize().multiply(4));
                    Fx.beam(chest, end, Particle.SONIC_BOOM, th, 1.6);
                    Fx.sound(chest, "ENTITY_WARDEN_SONIC_BOOM", 2.5f, 1f);
                    Vector line = end.toVector().subtract(chest.toVector());
                    double len = line.length();
                    Vector unit = line.clone().normalize();
                    for (Player p : service.fighters(f)) {
                        Vector rel = p.getEyeLocation().toVector().subtract(chest.toVector());
                        double along = rel.dot(unit);
                        if (along < 0 || along > len) continue;
                        if (rel.subtract(unit.clone().multiply(along)).lengthSquared() <= 2.6) {
                            hurt(f, p, 9);
                            if (service.mayHurt(f, p)) p.setVelocity(unit.clone().multiply(1.6).setY(0.5));
                        }
                    }
                });
            }
            case "skulls" -> {
                Fx.sound(at, "ENTITY_WITHER_SHOOT", 1.6f, 0.7f);
                List<Player> aimed = new ArrayList<>(targets.subList(0, Math.min(4, targets.size())));
                for (int wave = 0; wave < 3; wave++) {
                    int w = wave;
                    service.later(f, 6 + wave * 6L, () -> {
                        Fx.sound(boss.getLocation(), "ENTITY_WITHER_SHOOT", 1.4f, 0.8f + w * 0.1f);
                        for (Player p : aimed) {
                            if (!p.isValid() || !Bukkit.isOwnedByCurrentRegion(p) || !service.mayHurt(f, p)) continue;
                            Location from = boss.getEyeLocation().add(0, Math.max(0, big - 1), 0);
                            Vector dir = p.getEyeLocation().toVector().subtract(from.toVector());
                            if (dir.lengthSquared() < 0.01) continue;
                            WitherSkull skull = boss.launchProjectile(WitherSkull.class, dir.normalize().multiply(0.9)
                                    .add(new Vector(ThreadLocalRandom.current().nextGaussian() * 0.06, 0, ThreadLocalRandom.current().nextGaussian() * 0.06)));
                            skull.setCharged(w == 2 && f.phase > 0);
                            skull.setPersistent(false);
                            skull.setIsIncendiary(false);
                            skull.setYield(0);
                        }
                    });
                }
            }
            case "breath" -> {
                if (main == null) break;
                Vector dir = flat(at, main.getLocation());
                Location mouth = at.clone().add(0, Math.max(1, boss.getHeight() * 0.7 * big), 0).add(dir.clone().multiply(Math.max(1, big)));
                Fx.lineTelegraph(at, at.clone().add(dir.clone().multiply(12)), 5, th, 16);
                Fx.sound(at, "ENTITY_ENDER_DRAGON_GROWL", 1.6f, 0.9f);
                f.busyUntil = System.currentTimeMillis() + 2600;
                for (int i = 0; i < 9; i++) {
                    int k = i;
                    service.later(f, 16 + i * 3L, () -> {
                        Fx.sound(mouth, "ENTITY_ENDER_DRAGON_SHOOT", 1f, 0.8f + k * 0.03f);
                        for (int j = 1; j <= 12; j++) {
                            double spread = j * 0.22;
                            Location p = mouth.clone().add(dir.clone().multiply(j)).add(0, -j * 0.12, 0);
                            Fx.particle(at.getWorld(), Particle.DRAGON_BREATH, p, 4, spread, spread * 0.4, spread, 0.01, th);
                            if (j % 4 == 0) Fx.particle(at.getWorld(), th.spark(), p, 2, spread, 0.2, spread, 0.01, th);
                        }
                        for (Player p : service.fighters(f)) {
                            Vector rel = p.getLocation().toVector().subtract(at.toVector()).setY(0);
                            double d = rel.length();
                            if (d < 0.5 || d > 13) continue;
                            if (rel.normalize().dot(dir) > 0.82) { hurt(f, p, 2.2); if (service.mayHurt(f, p)) service.effect(p, "instant_damage", 1, 0); }
                        }
                    });
                }
            }
            case "spikes" -> {
                List<Location> spots = new ArrayList<>();
                for (Player p : targets.subList(0, Math.min(6, targets.size()))) spots.add(p.getLocation());
                if (spots.isEmpty()) spots.add(at.clone().add(3, 0, 0));
                Fx.sound(at, th.charge(), 1.4f, 0.6f);
                Fx.sound(at, "BLOCK_POINTED_DRIPSTONE_LAND", 1.2f, 0.5f);
                for (Location spot : spots) Fx.telegraph(spot, 2.2, th, 18);
                service.later(f, 18, () -> {
                    for (Location spot : spots) {
                        ThreadLocalRandom r = ThreadLocalRandom.current();
                        Fx.spike(spot, th.shard(), 2.6f, 18);
                        for (int i = 0; i < 4; i++) Fx.spike(spot.clone().add(r.nextDouble(-1.6, 1.6), 0, r.nextDouble(-1.6, 1.6)), th.shard(), 1.1f + r.nextFloat() * 1.2f, 14);
                        Fx.sound(spot, th.impact(), 1.2f, 0.9f);
                        Fx.blockDust(spot.clone().add(0, 0.4, 0), th.shard(), 20, 1.2);
                        for (Player p : service.fighters(f)) if (p.getLocation().distanceSquared(spot) <= 4.8) {
                            hurt(f, p, 5);
                            if (service.mayHurt(f, p)) p.setVelocity(new Vector(0, 0.9, 0));
                        }
                    }
                });
            }
            case "orbs" -> {
                int count = 6;
                Fx.sound(at, "BLOCK_BEACON_ACTIVATE", 1.2f, 1.6f);
                List<Player> aimed = new ArrayList<>(targets);
                for (int i = 0; i < 12; i++) {
                    int k = i;
                    service.later(f, 1 + i * 2L, () -> {
                        Location c = boss.getLocation().add(0, Math.max(1.4, boss.getHeight() * 0.6 * big), 0);
                        for (int j = 0; j < count; j++) {
                            double a = Math.PI * 2 * j / count + k * 0.35;
                            Location o = c.clone().add(Math.cos(a) * 2.4 * big, Math.sin(k * 0.5 + j) * 0.3, Math.sin(a) * 2.4 * big);
                            Fx.dust(o, th.accent(), 2.2f, 2, 0.05);
                            Fx.particle(o.getWorld(), th.spark(), o, 1, 0, 0, 0, 0, th);
                        }
                    });
                }
                service.later(f, 26, () -> {
                    Fx.sound(boss.getLocation(), "ENTITY_SHULKER_SHOOT", 1.4f, 1.2f);
                    for (int j = 0; j < Math.min(count, Math.max(1, aimed.size() * 2)); j++) {
                        Player p = aimed.isEmpty() ? null : aimed.get(j % aimed.size());
                        if (p == null || !p.isValid() || !Bukkit.isOwnedByCurrentRegion(p)) continue;
                        Location from = boss.getLocation().add(0, Math.max(1.4, boss.getHeight() * 0.6 * big), 0);
                        for (int s = 1; s <= 5; s++) {
                            int step = s;
                            service.later(f, s * 2L, () -> {
                                if (!p.isValid()) return;
                                Location to = p.getLocation().add(0, 1, 0);
                                Location pos = from.clone().add(to.toVector().subtract(from.toVector()).multiply(step / 5.0));
                                Fx.dust(pos, th.accent(), 2.4f, 4, 0.08);
                                Fx.particle(pos.getWorld(), th.spark(), pos, 2, 0.05, 0.05, 0.05, 0, th);
                                if (step == 5 && p.getLocation().distanceSquared(boss.getLocation()) < 900) {
                                    hurt(f, p, 3);
                                    Fx.sound(pos, th.impact(), 1f, 1.4f);
                                }
                            });
                        }
                    }
                });
            }
            case "gifts", "eggs", "sprinkles" -> {
                List<Location> spots = new ArrayList<>();
                ThreadLocalRandom rnd = ThreadLocalRandom.current();
                for (Player p : targets.subList(0, Math.min(5, targets.size()))) {
                    spots.add(p.getLocation());
                    if (!ability.equals("eggs")) spots.add(p.getLocation().add(rnd.nextInt(-3, 4), 0, rnd.nextInt(-3, 4)));
                }
                while (spots.size() < 3) spots.add(at.clone().add(rnd.nextInt(-7, 8), 0, rnd.nextInt(-7, 8)));
                String kind = ability;
                Fx.sound(at, kind.equals("gifts") ? "BLOCK_NOTE_BLOCK_BELL" : kind.equals("eggs") ? "ENTITY_CHICKEN_EGG" : "BLOCK_HONEY_BLOCK_SLIDE", 1.4f, 0.8f);
                if (kind.equals("gifts")) Fx.sound(at, "ENTITY_EVOKER_CELEBRATE", 1f, 0.7f);
                for (int i = 0; i < spots.size(); i++) {
                    Location spot = spots.get(i);
                    if (!Bukkit.isOwnedByCurrentRegion(spot)) continue;
                    Material block = kind.equals("gifts") ? (i % 2 == 0 ? Material.RED_SHULKER_BOX : Material.LIME_SHULKER_BOX)
                            : kind.equals("eggs") ? Material.WHITE_CONCRETE : CONCRETE[rnd.nextInt(CONCRETE.length)];
                    float size = kind.equals("sprinkles") ? 0.45f : kind.equals("eggs") ? 0.8f : 1f;
                    Fx.telegraph(spot, kind.equals("sprinkles") ? 2 : 2.8, th, 22 + i * 3);
                    service.later(f, 2 + i * 3L, () -> Fx.meteor(spot, block, th, 20, size, () -> {
                        World w = spot.getWorld();
                        switch (kind) {
                            case "gifts" -> {
                                Fx.particle(w, Particle.FIREWORK, spot.clone().add(0, 0.8, 0), 50, 0.6, 0.6, 0.6, 0.15, th);
                                Fx.particle(w, Particle.EXPLOSION, spot, 2, 0.4, 0.2, 0.4, 0, th);
                                Fx.sound(spot, "ENTITY_FIREWORK_ROCKET_LARGE_BLAST", 1.4f, 0.9f);
                                Fx.sound(spot, "ENTITY_FIREWORK_ROCKET_TWINKLE", 1f, 1.2f);
                                Fx.debris(spot, block, 4, 2.4, 2.2, 0.35f);
                            }
                            case "eggs" -> {
                                Fx.particle(w, Particle.POOF, spot.clone().add(0, 0.4, 0), 25, 0.5, 0.3, 0.5, 0.04, th);
                                Fx.sound(spot, "ENTITY_TURTLE_EGG_BREAK", 1.4f, 0.8f);
                                Fx.debris(spot, Material.WHITE_CONCRETE, 5, 1.6, 1.4, 0.25f);
                                if (rnd.nextInt(3) == 0) service.summonMinionsAt(f, spot, 1);
                            }
                            default -> {
                                Fx.particle(w, Particle.CLOUD, spot.clone().add(0, 0.3, 0), 14, 0.5, 0.2, 0.5, 0.02, th);
                                Fx.sound(spot, "BLOCK_SNOW_BREAK", 1.2f, 1.4f);
                                Fx.debris(spot, block, 3, 1.2, 0.9, 0.2f);
                            }
                        }
                        double r2 = kind.equals("sprinkles") ? 4 : 7.5;
                        for (Player p : service.fighters(f)) if (p.getLocation().distanceSquared(spot) <= r2) {
                            hurt(f, p, kind.equals("sprinkles") ? 3 : 5);
                            if (!service.mayHurt(f, p)) continue;
                            if (kind.equals("sprinkles")) { service.effect(p, "slowness", 50, 1); p.setFreezeTicks(Math.min(p.getMaxFreezeTicks() + 40, 180)); }
                            else knock(p, spot, 0.8, 0.6);
                        }
                    }));
                }
            }
            case "dive" -> service.dive(f, main);
            default -> { // roar
                Fx.sound(at, "ENTITY_WARDEN_ROAR", 1.4f, 0.8f);
                Fx.sound(at, th.charge(), 1.2f, 0.7f);
                Fx.particle(world, Particle.SONIC_BOOM, at.clone().add(0, Math.max(1.5, boss.getHeight() * 0.7 * big), 0), 1, 0, 0, 0, 0, th);
                for (int i = 0; i < 3; i++) {
                    int k = i;
                    service.later(f, 2 + i * 3L, () -> Fx.ring(boss.getLocation(), 2 + k * 3, th.main(), 2f, 30 + k * 10));
                }
                for (Player p : targets) if (service.mayHurt(f, p)) {
                    service.effect(p, "weakness", 100, 0);
                    if (p.getLocation().distanceSquared(at) < 49) knock(p, at, 0.7, 0.3);
                }
            }
        }
    }
}
