package com.cquests.npc;

import com.cquests.CQuestsPlugin;
import com.cquests.model.NpcDef;
import com.cquests.util.Sched;
import com.cquests.util.Text;
import net.kyori.adventure.text.Component;
import org.bukkit.Location;
import org.bukkit.entity.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/** One chapter-filtered nameplate per live quest NPC; speech text remains private. */
public final class NpcNameplates {
    public static final String FORMAT="<gold><bold><name></bold></gold>\n<gray>LEVEL <aqua><level></aqua></gray>";
    public static final String LEGACY="<white><name></white> <dark_gray>[<gray>Lv <level></gray>]</dark_gray>";
    private record Plate(LivingEntity npc,TextDisplay display,Location anchor) {}
    private final CQuestsPlugin plugin;
    private final Map<String,Plate> plates=new ConcurrentHashMap<>();
    private final Map<String,Set<UUID>> speakers=new ConcurrentHashMap<>();
    public NpcNameplates(CQuestsPlugin plugin){this.plugin=plugin;}
    public Component label(NpcDef npc){
        Component result=Text.mm(plugin.settings().npcNameFormat.replace("<name>",npc.name()).replace("<level>",Integer.toString(npc.level())).replace("<title>",Text.escape(npc.title())));
        return plugin.getConfig().getBoolean("npc.uppercase-names",true)?uppercase(result):result;
    }
    public static Component uppercase(Component value){
        Component result=value.children(value.children().stream().map(NpcNameplates::uppercase).toList());
        return result instanceof net.kyori.adventure.text.TextComponent text?text.content(text.content().toUpperCase(Locale.ROOT)):result;
    }
    public void spawn(NpcDef definition,LivingEntity npc,Location anchor){
        remove(definition.id());
        TextDisplay display=anchor.getWorld().spawn(anchor.clone().add(0,height(definition.id()),0),TextDisplay.class,d->{
            d.setPersistent(false);d.setVisibleByDefault(false);d.setBillboard(Display.Billboard.CENTER);d.setShadowed(true);d.setSeeThrough(false);d.setLineWidth(260);d.text(label(definition));
        });
        plates.put(definition.id(),new Plate(npc,display,anchor.clone()));
    }
    public void show(Player viewer,String id,boolean visible){Plate plate=plates.get(id);if(plate==null)return;if(visible)viewer.showEntity(plugin,plate.display());else viewer.hideEntity(plugin,plate.display());}
    public void begin(String id,UUID token){speakers.compute(id,(key,old)->{Set<UUID> next=new HashSet<>(old==null?Set.of():old);next.add(token);return Set.copyOf(next);});move(id);}
    public void end(String id,UUID token){speakers.computeIfPresent(id,(key,old)->{Set<UUID> next=new HashSet<>(old);next.remove(token);return next.isEmpty()?null:Set.copyOf(next);});move(id);}
    public double height(String id){return speakers.containsKey(id)?3.85:2.45;}
    private void move(String id){if(!plugin.isEnabled())return;Plate plate=plates.get(id);if(plate!=null)Sched.entity(plate.display(),()->{if(plates.get(id)==plate)plate.display().teleportAsync(plate.anchor().clone().add(0,height(id),0));});}
    public void remove(String id){Plate plate=plates.remove(id);if(plate!=null&&plugin.isEnabled())Sched.entity(plate.display(),plate.display()::remove);}
    public void clear(){for(String id:List.copyOf(plates.keySet()))remove(id);speakers.clear();}
}
