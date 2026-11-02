package com.cquests.progression;

import com.cquests.CQuestsPlugin;
import org.bukkit.configuration.file.YamlConfiguration;
import java.io.File;
import java.nio.file.Files;

/** Upgrade only the former shipped level cap; retain custom curves and every player's XP. */
public final class ProgressionUpgrade {
    private ProgressionUpgrade(){}
    public static void apply(CQuestsPlugin plugin){
        File marker=new File(plugin.getDataFolder(),".levels-1.4.0");if(marker.exists())return;
        File file=new File(plugin.getDataFolder(),"farming.yml");
        try{
            var yaml=new YamlConfiguration();yaml.load(file);
            if(yaml.getInt("levels.maximum",500)==100){
                var backup=file.toPath().resolveSibling("farming.yml.before-1.4.0");
                if(!Files.exists(backup))Files.copy(file.toPath(),backup);
                yaml.set("levels.maximum",500);yaml.save(file);
            }
            Files.writeString(marker.toPath(),"Expanded the former default level cap. Existing XP and quest progress retained.\n");
        }catch(Exception e){plugin.getLogger().warning("Level-cap migration deferred; existing data retained: "+e.getMessage());}
    }
}
