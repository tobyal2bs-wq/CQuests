package com.cquests.npc;

import com.cquests.T;

import com.cquests.CQuestsPlugin;
import com.cquests.model.NpcDef;
import com.cquests.util.Text;
import org.bukkit.command.CommandSender;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;
import java.io.File;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;

/** Operator-owned cosmetic overrides. IDs, objectives and player progress are never rewritten. */
public final class NpcCustomization {
    private final CQuestsPlugin plugin;
    private final File file;
    private final ExecutorService writer=Executors.newSingleThreadExecutor(r->{var t=new Thread(r,"CQuests-character-writer");t.setDaemon(true);return t;});
    private volatile Map<String,Map<String,Object>> values=Map.of();
    private int pending;private boolean stopped;
    public NpcCustomization(CQuestsPlugin plugin){this.plugin=plugin;file=new File(plugin.getDataFolder(),"characters.yml");reload();}
    private static String key(String id){return id.startsWith("companion_")?"pip":id;}
    public synchronized void reload(){
        if(pending>0)return;
        var yaml=YamlConfiguration.loadConfiguration(file);var root=yaml.getConfigurationSection("characters");var next=new HashMap<String,Map<String,Object>>();
        if(root!=null)for(String id:root.getKeys(false)){
            var section=root.getConfigurationSection(id);if(section!=null&&id.matches("[a-z0-9_-]{1,80}"))next.put(id,Map.copyOf(section.getValues(false)));
        }values=Map.copyOf(next);
    }
    public String text(String id,String field,String fallback){Object value=values.getOrDefault(key(id),Map.of()).get(field);return value instanceof String s?s:fallback;}
    public List<String> lines(String id,String field,List<String> fallback){
        Object value=values.getOrDefault(key(id),Map.of()).get(field);
        return value instanceof List<?> list?list.stream().filter(String.class::isInstance).map(String.class::cast).limit(20).toList():fallback;
    }
    public NpcDef apply(NpcDef n){
        return new NpcDef(n.id(),text(n.id(),"name",n.name()),text(n.id(),"title",n.title()),n.profession(),n.skin(),n.level(),n.act(),n.personal(),n.daily(),n.baby(),n.playerSkin(),lines(n.id(),"intro",n.intro()),lines(n.id(),"idle",n.idle()));
    }
    public String label(String id,String fallback){return text(id,"prefix","")+text(id,"name",fallback);}
    public net.kyori.adventure.text.Component merchantLabel(String id,String name,String status){
        String format=text(id,"format","<bold><prefix><name></bold>\n<gray><title></gray>");
        if(!format.contains("<prefix>"))format="<prefix>"+format;
        var component=Text.mm(format.replace("<prefix>",text(id,"prefix","")).replace("<name>",text(id,"name",name)).replace("<title>",status).replace("<level>","0"));
        return plugin.getConfig().getBoolean("npc.uppercase-names",true)?NpcNameplates.uppercase(component):component;
    }
    public String speechPrefix(NpcDef npc){return text(npc.id(),"speech-prefix","<gold><bold><name></bold></gold><gray> › </gray>").replace("<name>",label(npc.id(),npc.name()));}
    public void command(CommandSender sender,String[] args){
        if(sender instanceof Player player?!player.isOp():!(sender instanceof org.bukkit.command.ConsoleCommandSender)){plugin.send(sender,T.t("npc-customization.only-an-operator-or-the", "<red>Only an operator or the console can edit characters."));return;}
        if(args.length<3){help(sender);return;}
        String id=args[1].toLowerCase(Locale.ROOT),field=args[2].toLowerCase(Locale.ROOT);
        var npc=plugin.npcs().get(id);if(npc!=null)id=npc.id();
        if(npc==null&&plugin.merchants().get(id)==null&&!id.equals("pip")){plugin.send(sender,T.t("npc-customization.unknown-character-use-a-quest", "<red>Unknown character. Use a quest NPC ID, merchant ID, or pip."));return;}
        if(!Set.of("name","title","prefix","format","speech-prefix","intro","idle","arrival","reset").contains(field)){help(sender);return;}
        if(!field.equals("reset")&&args.length<4){help(sender);return;}
        String value=String.join(" ",Arrays.copyOfRange(args,3,args.length));
        if(field.equals("format"))value=value.replace("\\n","\n");
        if(value.length()>1600||(field.equals("name")&&Text.plain(Text.mm(value)).isBlank())){plugin.send(sender,T.t("npc-customization.use-a-visible-name-and", "<red>Use a visible name and at most 1600 characters."));return;}
        Object replacement=Set.of("intro","idle").contains(field)?(value.equalsIgnoreCase("none")?List.of():Arrays.stream(value.split("\\|",-1)).map(String::trim).filter(s->!s.isEmpty()).limit(20).toList()):field.equals("prefix")&&value.equalsIgnoreCase("none")?"":value;
        if(!save(id,field,replacement)){plugin.send(sender,T.t("npc-customization.character-editor-is-shutting-down", "<red>Character editor is shutting down."));return;}
        if(plugin.npcs()!=null)plugin.npcs().refresh();plugin.nameplates().refresh();plugin.merchants().refreshLabels();if(plugin.tracker()!=null)plugin.tracker().invalidate();
        plugin.send(sender,T.t("npc-customization.updated-existing-quest-progress-is", "<green>Updated <id> • <field>. Existing quest progress is unchanged.", "id", Text.escape(id), "field", field));
    }
    private void help(CommandSender sender){plugin.send(sender,T.t("npc-customization.cq-character-name-title-prefix", "<white>/cq character <id> name|title|prefix|format|speech-prefix <MiniMessage text>\n<white>/cq character <id> intro|idle <sentence | another sentence>\n<white>/cq character <id> reset\n<gray>Use none to clear a prefix. Format placeholders: <name>, <level>, <title>, <prefix>. Quest NPCs, merchants and pip are supported. A new name shows everywhere: name tags, chat, quest text, the tracker, directions, mail and menus. Changes affect the next conversation.\n<white>/cq npc rename <id> <name> <gray>is a shortcut for the name."));}
    private synchronized boolean save(String id,String field,Object replacement){
        if(stopped)return false;
        var next=new HashMap<>(values);var character=new HashMap<>(next.getOrDefault(id,Map.of()));
        if(field.equals("reset"))next.remove(id);else{character.put(field,replacement);next.put(id,Map.copyOf(character));}values=Map.copyOf(next);
        var yaml=new YamlConfiguration();values.forEach((name,fields)->fields.forEach((k,v)->yaml.set("characters."+name+"."+k,v)));
        String snapshot=yaml.saveToString();pending++;
        writer.execute(()->{try{
            Path temp=file.toPath().resolveSibling("characters.yml.tmp");Files.writeString(temp,snapshot);
            try{Files.move(temp,file.toPath(),StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);}catch(AtomicMoveNotSupportedException e){Files.move(temp,file.toPath(),StandardCopyOption.REPLACE_EXISTING);}
        }catch(Exception e){plugin.getLogger().severe("Character save failed: "+e.getMessage());}finally{synchronized(this){pending--;}}});
        return true;
    }
    public void shutdown(){synchronized(this){stopped=true;writer.shutdown();}try{if(!writer.awaitTermination(10,TimeUnit.SECONDS))plugin.getLogger().warning("Character saves did not finish before shutdown.");}catch(InterruptedException e){Thread.currentThread().interrupt();}}
}
