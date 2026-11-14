package com.cbosses.hook;

import com.cbosses.CBossesPlugin;
import com.cbosses.fight.BossDef;
import me.clip.placeholderapi.expansion.PlaceholderExpansion;
import org.bukkit.OfflinePlayer;
import org.jetbrains.annotations.NotNull;

/**
 * %cbosses_next% time until the weekly boss, %cbosses_next_boss% its name, %cbosses_alive% the boss alive now,
 * %cbosses_chapter_<n>% "yes" when the player beat that chapter's boss, %cbosses_count% bosses loaded.
 */
public final class Placeholders extends PlaceholderExpansion {
    private final CBossesPlugin plugin;

    public Placeholders(CBossesPlugin plugin) { this.plugin = plugin; }

    @Override public @NotNull String getIdentifier() { return "cbosses"; }
    @Override public @NotNull String getAuthor() { return "clarx"; }
    @Override public @NotNull String getVersion() { return plugin.getPluginMeta().getVersion(); }
    @Override public boolean persist() { return true; }

    @Override
    public String onRequest(OfflinePlayer player, @NotNull String id) {
        var s = plugin.service();
        switch (id) {
            case "next": return s.nextText();
            case "next_boss": return s.upcomingName();
            case "alive": return s.aliveName();
            case "alive_bool": return s.alive() ? "yes" : "no";
            case "count": return Integer.toString(s.defs().size());
            default: break;
        }
        if (id.startsWith("chapter_") && player != null) {
            try {
                int n = Integer.parseInt(id.substring(8));
                return plugin.chapters().beat(player.getUniqueId(), n) ? "yes" : "no";
            } catch (NumberFormatException e) { return ""; }
        }
        if (id.startsWith("name_")) {
            BossDef d = s.def(id.substring(5));
            return d == null ? "" : com.cbosses.util.Text.plain(com.cbosses.util.Text.mm(d.name()));
        }
        return null;
    }
}
