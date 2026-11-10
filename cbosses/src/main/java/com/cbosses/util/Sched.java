package com.cbosses.util;

import io.papermc.paper.threadedregions.scheduler.ScheduledTask;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.entity.Entity;
import org.bukkit.plugin.Plugin;

import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;

/**
 * Thin wrapper over the region-aware schedulers. Paper ships these too, so the same
 * code runs on Paper, Folia and forks such as Leaf without a platform check.
 */
public final class Sched {

    private static Plugin plugin;

    private Sched() {
    }

    public static void init(Plugin owner) {
        plugin = owner;
    }

    /** Runs on the global region thread (main thread on Paper). Console commands must go here. */
    public static void global(Runnable task) {
        Bukkit.getGlobalRegionScheduler().execute(plugin, task);
    }

    public static ScheduledTask globalTimer(Consumer<ScheduledTask> task, long delayTicks, long periodTicks) {
        return Bukkit.getGlobalRegionScheduler().runAtFixedRate(plugin, task, Math.max(1, delayTicks), Math.max(1, periodTicks));
    }

    /** Runs on the thread that owns the region containing {@code location}. */
    public static void at(Location location, Runnable task) {
        Bukkit.getRegionScheduler().execute(plugin, location, task);
    }

    /** Runs on the thread that owns {@code entity}; silently skipped if the entity is gone. */
    public static void entity(Entity entity, Runnable task) {
        entity.getScheduler().run(plugin, t -> task.run(), null);
    }

    public static void entityLater(Entity entity, long delayTicks, Runnable task) {
        entity.getScheduler().runDelayed(plugin, t -> task.run(), null, Math.max(1, delayTicks));
    }

    public static void async(Runnable task) {
        Bukkit.getAsyncScheduler().runNow(plugin, t -> task.run());
    }

    public static ScheduledTask asyncTimer(Runnable task, long periodSeconds) {
        return Bukkit.getAsyncScheduler().runAtFixedRate(plugin, t -> task.run(), periodSeconds, periodSeconds, TimeUnit.SECONDS);
    }
}
