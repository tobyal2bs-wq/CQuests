package com.cquests.adventure;

import com.cquests.CQuestsPlugin;
import com.cquests.data.PlayerData;
import com.cquests.gui.LockedMenu;
import com.cquests.gui.QuestMenu;
import com.cquests.model.NpcDef;
import com.cquests.util.Text;
import org.bukkit.*;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;
import org.bukkit.event.inventory.ClickType;
import org.bukkit.inventory.Inventory;
import java.io.File;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/** Authored memories, keyed by player UUID. No external model or chat recording. */
public final class NpcMemory {
    public record Decision(String quest, String npc, List<String> family, String prompt,
                           String kind, String selfish, String warm, String wary,
                           String familyWarm, String familyWary) {}
    private final CQuestsPlugin plugin;
    private volatile List<Decision> decisions = List.of();
    private final Map<UUID, Map<String,Long>> greeted = new ConcurrentHashMap<>();
    public NpcMemory(CQuestsPlugin plugin) { this.plugin=plugin; reload(); }
    public void reload() {
        var yaml=YamlConfiguration.loadConfiguration(new File(plugin.getDataFolder(),"memories.yml"));
        var loaded=new ArrayList<Decision>();var section=yaml.getConfigurationSection("decisions");
        if(yaml.getBoolean("enabled",true)&&section!=null)for(String id:section.getKeys(false)) {
            String p="decisions."+id+".";
            if(!id.matches("[a-z0-9_-]{1,80}"))continue;
            loaded.add(new Decision(id,yaml.getString(p+"npc",""),List.copyOf(yaml.getStringList(p+"family")),
                    yaml.getString(p+"prompt","What will you tell them?"),yaml.getString(p+"kind","You can count on me."),
                    yaml.getString(p+"selfish","Look after your own affairs."),yaml.getString(p+"warm","I remember your kindness, {player}."),
                    yaml.getString(p+"wary","I remember what you said, {player}."),yaml.getString(p+"family-warm","My family spoke well of you, {player}."),
                    yaml.getString(p+"family-wary","My family told me what happened, {player}. I'm keeping my distance.")));
        }
        decisions=List.copyOf(loaded);greeted.clear();
    }
    public boolean near(Player player,String npc) {
        var def=plugin.npcs().get(npc);var point=plugin.spawns().points().get(npc);
        if(def==null||point==null||!plugin.questManager().shouldSee(plugin.questManager().data(player),def))return false;
        var at=point.location();return at!=null&&at.getWorld().equals(player.getWorld())&&at.distanceSquared(player.getLocation())<=64;
    }
    public boolean offer(Player player,NpcDef npc) {
        var data=plugin.questManager().data(player);
        for(var decision:decisions)if(decision.npc().equals(npc.id())&&data.isCompleted(decision.quest())&&data.decision(decision.quest())==null) {
            plugin.speech().start(player,npc,List.of(plugin.questManager().fill(decision.prompt(),player)),()->{
                if(near(player,npc.id())&&data.decision(decision.quest())==null)new ChoiceMenu(player,decision).open();
            });
            return true;
        }
        return false;
    }
    public String greeting(Player player,String npc) {
        long now=System.nanoTime();var times=greeted.computeIfAbsent(player.getUniqueId(),ignored->new ConcurrentHashMap<>());
        if(now<times.getOrDefault(npc,0L))return null;
        var data=plugin.questManager().data(player);
        String line=remember(data,npc,decisions);
        if(line==null)for(var quest:plugin.quests().story())if(quest.giver().equals(npc)&&data.isCompleted(quest.id()))
            line="Back again, {player}? I haven't forgotten your help with "+Text.escape(Text.plain(Text.mm(quest.name())))+".";
        if(line==null&&data.hasMet(npc))line="Good to see you again, {player}. How is the road treating you?";
        if(line!=null)times.put(npc,now+60_000_000_000L);
        return line;
    }
    public static String remember(PlayerData data,String npc,List<Decision> definitions) {
        String result=null;
        for(var d:definitions) {
            String choice=data.decision(d.quest());if(choice==null)continue;
            boolean kind=choice.equals("kind");
            if(d.npc().equals(npc))result=kind?d.warm():d.wary();
            else if(d.family().contains(npc))result=kind?d.familyWarm():d.familyWary();
        }
        return result;
    }
    public String companionLine(PlayerData data) {
        if("selfish".equals(data.decision("story_martha")))return "Martha told Steve what you said. I'll still help you through this, but promises matter here.";
        if("kind".equals(data.decision("story_martha")))return "Steve says Martha is sleeping again. You did that. Now, where are we headed?";
        return "I'll watch your back. You take the lead.";
    }
    public void forget(Player player) { greeted.remove(player.getUniqueId()); }
    private final class ChoiceMenu implements LockedMenu {
        private final Player player;private final Decision decision;private final Inventory inventory;
        private boolean used;
        ChoiceMenu(Player player,Decision decision) {
            this.player=player;this.decision=decision;
            inventory=Bukkit.createInventory(this,27,Text.mm("<dark_gray>A promise to remember"));
            for(int i=0;i<27;i++)inventory.setItem(i,QuestMenu.item(Material.GRAY_STAINED_GLASS_PANE," ",List.of()));
            inventory.setItem(4,QuestMenu.item(Material.WRITABLE_BOOK,"<gold>They will remember your answer",DialogueLines.wrap(plugin.questManager().fill(decision.prompt(),player))));
            inventory.setItem(11,QuestMenu.item(Material.SUNFLOWER,"<white>"+Text.escape(decision.kind()),List.of("<gray>Give them your word.")));
            inventory.setItem(15,QuestMenu.item(Material.FLINT,"<white>"+Text.escape(decision.selfish()),List.of("<gray>Put yourself first.")));
            inventory.setItem(26,QuestMenu.item(Material.BARRIER,"<gray>I need a moment",List.of("<gray>You can answer when we speak again.")));
        }
        void open(){player.openInventory(inventory);}
        public UUID viewer(){return player.getUniqueId();}
        public Inventory getInventory(){return inventory;}
        public void click(int slot,ClickType type) {
            if(slot==26){player.closeInventory();return;}
            if(used||(slot!=11&&slot!=15)||!decisions.contains(decision)||!near(player,decision.npc()))return;
            used=true;var data=plugin.questManager().data(player);
            if(!data.decide(decision.quest(),slot==11?"kind":"selfish")){player.closeInventory();return;}
            plugin.store().saveNow(data);plugin.mail().notifyNew(player);player.closeInventory();
            plugin.send(player,"<gold>"+Text.escape(plugin.npcs().get(decision.npc()).name())+" <gray>will remember that.");
            var npc=plugin.npcs().get(decision.npc());
            plugin.speech().start(player,npc,List.of(plugin.questManager().fill(slot==11?decision.warm():decision.wary(),player)),()->{});
        }
    }
    private static final class DialogueLines {
        static List<String> wrap(String text) {
            return com.cquests.dialogue.DialogueView.paginate(List.of(text),44,8).stream().flatMap(List::stream).map(s->"<white>"+Text.escape(s)).toList();
        }
    }
}
