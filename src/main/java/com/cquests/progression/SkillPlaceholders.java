package com.cquests.progression;

import com.cquests.CQuestsPlugin;
import me.clip.placeholderapi.expansion.PlaceholderExpansion;
import org.bukkit.OfflinePlayer;
import org.jetbrains.annotations.NotNull;

/** Cached reads only: placeholder calls never load player files. */
public final class SkillPlaceholders extends PlaceholderExpansion {
    private final CQuestsPlugin plugin;
    public SkillPlaceholders(CQuestsPlugin plugin){this.plugin=plugin;}
    public @NotNull String getIdentifier(){return "cquests";}
    public @NotNull String getAuthor(){return "CQuests";}
    public @NotNull String getVersion(){return plugin.getPluginMeta().getVersion();}
    public boolean persist(){return true;}
    public String onRequest(OfflinePlayer player,@NotNull String params){
        if(player==null)return "";
        var data=plugin.store().cached(player.getUniqueId());if(data==null)return "0";
        return switch(params.toLowerCase(java.util.Locale.ROOT)){
            case "level" -> Integer.toString(plugin.progression().level(data));
            case "xp" -> Long.toString(data.skillXp());
            case "xp_required" -> Long.toString(plugin.progression().curve().remaining(data.skillXp()));
            case "xp_progress" -> Long.toString(Math.round(plugin.progression().curve().progress(data.skillXp())*100));
            case "sunflowers" -> Long.toString(data.sunflowers());
            case "wheat" -> Long.toString(data.wheatHarvested());
            case "hoe_tier" -> Integer.toString(data.hoeTier());
            default -> null;
        };
    }
}
