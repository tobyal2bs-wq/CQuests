package com.cbosses.fight;

import com.cbosses.arena.Arena;
import com.cbosses.model.BossModel;
import net.kyori.adventure.bossbar.BossBar;
import org.bukkit.Particle;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Mob;

import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

/** One running boss fight. */
public final class Fight {
    /** Set when the fight is private to its owner (a chapter boss): the Privacy circle's key. */
    public volatile String privateZone;
    public final String key;
    public final BossDef def;
    public final Arena arena;
    /** A test or self-test fight: nothing is paid. */
    public final boolean test;
    public final UUID tester;
    /** A chapter fight belongs to the player who finished the chapter; null for public fights. */
    public final UUID owner;
    public final Mob boss;
    public final double max;
    public final BossBar bar;
    public final Theme theme;
    /** Minecraft caps max health at 1024; bigger bosses take proportionally less damage instead. */
    public final double ratio;
    public final List<Entity> parts = new CopyOnWriteArrayList<>();
    public final List<Mob> minions = new CopyOnWriteArrayList<>();
    public final Map<UUID, Double> damage = new ConcurrentHashMap<>();
    public final Map<UUID, String> names = new ConcurrentHashMap<>();
    public final Set<UUID> viewers = ConcurrentHashMap.newKeySet();
    public final long born = System.currentTimeMillis();
    public volatile long lastPlayer = System.currentTimeMillis();
    long nextAbility, nextDash, busyUntil;
    /** How many of the boss's phases (health thresholds) have been passed. */
    int phase;
    int heals, ticks;
    long shownHealth = -1;
    boolean introDone;
    Particle aura = Particle.FLAME;
    /** Where a flying boss is heading, and the angle it circles its target at. */
    double orbit;
    int swoop;
    public volatile boolean over;
    public volatile String endReason;
    public volatile String killer;
    int chunkX, chunkZ, chunkR;
    String chunkWorld;
    /** The block model drawn over the invisible mob, or null for a plain mob boss. */
    public volatile BossModel model;
    /** The other body of a two-body boss (both fight on their own and are beaten together), or null. */
    public volatile Fight partner;
    /** Whose rewards and chapter this fight pays when it is the last body standing. */
    public volatile BossDef payDef;
    /** How many times it has evolved, whether it will, and when it next does. power multiplies all its damage. */
    public volatile int stage;
    boolean evolves;
    long nextEvolve;
    public volatile double power = 1;

    Fight(String key, BossDef def, Arena arena, boolean test, UUID tester, UUID owner, Mob boss, double max, BossBar bar, double health) {
        this.key = key; this.def = def; this.arena = arena; this.test = test; this.tester = tester; this.owner = owner;
        this.boss = boss; this.max = max; this.bar = bar;
        this.theme = Theme.of(def.theme());
        this.ratio = Math.max(1, health / Math.max(1, max));
        this.payDef = def;
    }

    public double speedFactor() {
        return Math.pow(0.82, phase);
    }

    public boolean busy() { return System.currentTimeMillis() < busyUntil; }
}
