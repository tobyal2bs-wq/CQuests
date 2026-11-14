package com.cbosses.api;

import org.bukkit.Location;
import org.bukkit.event.Event;
import org.bukkit.event.HandlerList;
import org.jetbrains.annotations.NotNull;

import java.util.List;
import java.util.UUID;

/** Called when a boss is beaten, before rewards are paid. */
public final class BossDefeatEvent extends Event {
    private static final HandlerList HANDLERS = new HandlerList();
    private final String boss;
    private final Location location;
    private final List<UUID> ranking;
    private final UUID owner;
    private final boolean test;

    public BossDefeatEvent(String boss, Location location, List<UUID> ranking, UUID owner, boolean test) {
        super(!org.bukkit.Bukkit.isPrimaryThread());
        this.boss = boss; this.location = location; this.ranking = List.copyOf(ranking); this.owner = owner; this.test = test;
    }

    public String getBoss() { return boss; }
    public Location getLocation() { return location.clone(); }
    /** Players by damage dealt, most first. */
    public List<UUID> getRanking() { return ranking; }
    /** The player a chapter boss belonged to, or null. */
    public UUID getOwner() { return owner; }
    public boolean isTest() { return test; }
    @Override public @NotNull HandlerList getHandlers() { return HANDLERS; }
    public static HandlerList getHandlerList() { return HANDLERS; }
}
