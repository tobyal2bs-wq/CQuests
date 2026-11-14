package com.cbosses.api;

import org.bukkit.Location;
import org.bukkit.entity.Player;
import org.bukkit.event.Cancellable;
import org.bukkit.event.Event;
import org.bukkit.event.HandlerList;
import org.jetbrains.annotations.NotNull;

/** Called before a boss starts appearing (its omen). Cancel it to stop the boss. */
public final class BossSpawnEvent extends Event implements Cancellable {
    private static final HandlerList HANDLERS = new HandlerList();
    private final String boss;
    private final Location location;
    private final Player owner;
    private final boolean test;
    private boolean cancelled;

    public BossSpawnEvent(String boss, Location location, Player owner, boolean test) {
        super(!org.bukkit.Bukkit.isPrimaryThread());
        this.boss = boss; this.location = location; this.owner = owner; this.test = test;
    }

    /** The boss id from bosses.yml. */
    public String getBoss() { return boss; }
    public Location getLocation() { return location.clone(); }
    /** The player a chapter boss belongs to, or null for a world boss. */
    public Player getOwner() { return owner; }
    public boolean isTest() { return test; }
    @Override public boolean isCancelled() { return cancelled; }
    @Override public void setCancelled(boolean cancel) { cancelled = cancel; }
    @Override public @NotNull HandlerList getHandlers() { return HANDLERS; }
    public static HandlerList getHandlerList() { return HANDLERS; }
}
