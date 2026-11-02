package com.cquests.merchant;

import com.cquests.util.Sched;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.entity.Player;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/** Private floor markers: never edits the world, produces drops or grants build access. */
final class TrailPreview {
    private final Map<UUID,Map<Location,Boolean>> viewers=new ConcurrentHashMap<>();
    void show(Player player,Location feet){
        if(!player.isOnline()||!MerchantService.canEdit(player)||!player.getWorld().equals(feet.getWorld()))return;
        Map<Location,Boolean> marks=viewers.computeIfAbsent(player.getUniqueId(),id->{
            Map<Location,Boolean> fresh=new ConcurrentHashMap<>();
            Sched.entityLater(player,2400,()->{if(viewers.remove(id,fresh))restore(player,fresh);});return fresh;
        });
        Location floor=feet.toBlockLocation().subtract(0,1,0);floor.setYaw(0);floor.setPitch(0);
        if(marks.size()>=64||marks.putIfAbsent(floor,true)!=null)return;
        player.sendBlockChange(floor,Material.GOLD_BLOCK.createBlockData());
    }
    void clear(Player player){var marks=viewers.remove(player.getUniqueId());if(marks!=null)restore(player,marks);}
    private void restore(Player player,Map<Location,Boolean> marks){
        for(Location loc:marks.keySet())Sched.at(loc,()->{
            if(!loc.getWorld().isChunkLoaded(loc.getBlockX()>>4,loc.getBlockZ()>>4))return;
            var data=loc.getBlock().getBlockData();Sched.entity(player,()->{
                var current=viewers.get(player.getUniqueId());
                if(player.isOnline()&&player.getWorld().equals(loc.getWorld())&&(current==null||!current.containsKey(loc)))player.sendBlockChange(loc,data);
            });
        });
    }
    void discard(){viewers.clear();}
    void clearAll(){for(UUID id:List.copyOf(viewers.keySet())){Player p=Bukkit.getPlayer(id);if(p==null)viewers.remove(id);else Sched.entity(p,()->clear(p));}}
}
