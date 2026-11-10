package com.cbosses.api;

import com.cbosses.CBossesPlugin;
import com.cbosses.fight.BossDef;
import org.bukkit.entity.Player;

import java.util.List;

/** A small API for other plugins: {@code CBossesAPI.get()} after CBosses has enabled. */
public final class CBossesAPI {
    private final CBossesPlugin plugin;

    public CBossesAPI(CBossesPlugin plugin) { this.plugin = plugin; }

    public static CBossesAPI get() { return CBossesPlugin.instance() == null ? null : CBossesPlugin.instance().api(); }

    public List<String> bosses() { return plugin.service().ids(); }

    public boolean isAlive(String boss) { return plugin.service().alive(boss); }

    /** Spawns a boss at an arena. False when it could not start. */
    public boolean spawn(String boss, String arena) {
        BossDef def = plugin.service().def(boss);
        var a = plugin.service().arena(arena, false);
        return def != null && a != null && plugin.service().spawn(def, a, null, false, null);
    }

    /** Sends a chapter boss after a player, as if they had just finished that chapter. */
    public boolean chapterBoss(Player player, int chapter) { return plugin.chapters().trigger(player, chapter, true); }
}
