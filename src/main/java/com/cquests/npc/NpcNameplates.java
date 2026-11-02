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
    private record Plate(LivingEntity npc,TextDisplay display,Location anchor,NpcDef definition) {}
    private final CQuestsPlugin plugin;
    private final Map<String,Plate> plates=new ConcurrentHashMap<>();
    private final Map<String,Map<UUID,Integer>> speakers=new ConcurrentHashMap<>();
    public NpcNameplates(CQuestsPlugin plugin){this.plugin=plugin;}
    public Component label(NpcDef npc){
        if(plugin.characters()!=null)npc=plugin.characters().apply(npc);
        int chapter=plugin.quests()==null?1:plugin.quests().firstChapter(npc.id());
        int level=npc.daily()?plugin.settings().dailyMinLevel:Math.max(npc.level(),plugin.settings().chapterLevels.getOrDefault(chapter,0));
        String format=plugin.settings().npcNameFormat;
        if(format.equals(FORMAT)){
            String color=npc.daily()?"gold":switch(chapter){case 2->"green";case 3->"aqua";case 4->"light_purple";case 5->"red";default->"yellow";};
            format=format.replace("<gold>","<"+color+">").replace("</gold>","</"+color+">");
        }
        if(plugin.characters()!=null)format=plugin.characters().text(npc.id(),"format",format);
        String prefix=plugin.characters()==null?"":plugin.characters().text(npc.id(),"prefix","");
        if(!format.contains("<prefix>"))format="<prefix>"+format;
        Component result=Text.mm(format.replace("<prefix>",prefix).replace("<name>",npc.name()).replace("<level>",Integer.toString(level)).replace("<title>",Text.escape(npc.title())));
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
        plates.put(definition.id(),new Plate(npc,display,anchor.clone(),definition));
    }
    public void show(Player viewer,String id,boolean visible){Plate plate=plates.get(id);if(plate==null)return;if(visible)viewer.showEntity(plugin,plate.display());else viewer.hideEntity(plugin,plate.display());}
    /** Moving companions use the same two-line plate, visible only to their owner. */
    public void follow(String id,Location at){
        Plate old=plates.get(id);if(old==null)return;
        Plate next=new Plate(old.npc(),old.display(),at.clone(),old.definition());
        if(plates.replace(id,old,next))move(id);
    }
    public void begin(String id,UUID token){speakers.compute(id,(key,old)->{var next=new HashMap<UUID,Integer>(old==null?Map.of():old);next.put(token,1);return Map.copyOf(next);});move(id);}
    public void lines(String id,UUID token,int rows){speakers.computeIfPresent(id,(key,old)->{if(!old.containsKey(token))return old;var next=new HashMap<>(old);next.put(token,Math.max(1,Math.min(4,rows)));return Map.copyOf(next);});move(id);}
    public void end(String id,UUID token){speakers.computeIfPresent(id,(key,old)->{var next=new HashMap<>(old);next.remove(token);return next.isEmpty()?null:Map.copyOf(next);});move(id);}
    public double height(String id){var rows=speakers.get(id);return rows==null?2.3:2.55+.225*(rows.values().stream().mapToInt(Integer::intValue).max().orElse(1)-1);}
    private void move(String id){if(!plugin.isEnabled())return;Plate plate=plates.get(id);if(plate!=null)Sched.entity(plate.display(),()->{if(plates.get(id)==plate)plate.display().teleportAsync(plate.anchor().clone().add(0,height(id),0));});}
    public void remove(String id){Plate plate=plates.remove(id);if(plate!=null&&plugin.isEnabled())Sched.entity(plate.display(),plate.display()::remove);}
    public void refresh(){for(var entry:plates.entrySet()){var def=plugin.npcs().get(entry.getKey());var plate=entry.getValue();if(def==null&&entry.getKey().startsWith("companion_")&&plugin.characters()!=null)def=plugin.characters().apply(plate.definition());if(def!=null){var text=label(def);Sched.entity(plate.display(),()->{if(plates.get(entry.getKey())==plate)plate.display().text(text);});}}}
    public void clear(){for(String id:List.copyOf(plates.keySet()))remove(id);speakers.clear();}
}
