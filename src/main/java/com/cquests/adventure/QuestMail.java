package com.cquests.adventure;

import com.cquests.CQuestsPlugin;
import com.cquests.data.PlayerData;
import com.cquests.gui.LockedMenu;
import com.cquests.gui.QuestMenu;
import com.cquests.util.Text;
import org.bukkit.*;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;
import org.bukkit.event.inventory.ClickType;
import org.bukkit.inventory.Inventory;
import java.io.File;
import java.util.*;

/** Letters are derived from the player's ledger; opening one never pays repeatable rewards. */
public final class QuestMail {
    public record Letter(String id,String sender,String subject,String quest,String decision,String met,long wheat,List<String> body) {
        public boolean eligible(PlayerData data) {
            return (quest.isEmpty() || data.isCompleted(quest)) && (decision.isEmpty() || decision.equals(data.decision(quest)))
                    && (met.isEmpty() || data.hasMet(met)) && data.wheatHarvested() >= wheat;
        }
    }
    private final CQuestsPlugin plugin;
    private volatile List<Letter> letters=List.of();
    private final Map<UUID,Long> notified=new java.util.concurrent.ConcurrentHashMap<>();
    public QuestMail(CQuestsPlugin plugin){this.plugin=plugin;reload();}
    public void reload(){
        var yaml=YamlConfiguration.loadConfiguration(new File(plugin.getDataFolder(),"letters.yml"));
        var root=yaml.getConfigurationSection("letters");var next=new ArrayList<Letter>();
        if(yaml.getBoolean("enabled",true)&&root!=null)for(String id:root.getKeys(false)){
            if(!id.matches("[a-z0-9_-]{1,80}")||next.size()>=512)continue;String p="letters."+id+".";
            next.add(new Letter(id,yaml.getString(p+"sender","A friend"),yaml.getString(p+"subject","A letter for you"),
                    yaml.getString(p+"quest",""),yaml.getString(p+"decision",""),yaml.getString(p+"met",""),
                    Math.max(0,yaml.getLong(p+"wheat",0)),yaml.getStringList(p+"body").stream().limit(20).map(s->s.substring(0,Math.min(1600,s.length()))).toList()));
        }letters=List.copyOf(next);
    }
    public void notifyNew(Player player){
        var data=plugin.questManager().data(player);long unread=letters.stream().filter(l->l.eligible(data)&&!data.letterRead(l.id())).count();
        Long old=notified.put(player.getUniqueId(),unread);
        if(unread>0&&(old==null||unread>old))plugin.send(player,"<yellow>You have "+unread+" unread letter"+(unread==1?"":"s")+". <white>/quest mail");
    }
    public void forget(Player player){notified.remove(player.getUniqueId());}
    public void open(Player player){new Mailbox(player,0).open();}
    public void discovered(Player player){
        var data=plugin.questManager().data(player);
        if(data.wheatHarvested()%750!=0)return;
        plugin.store().saveNow(data);
        plugin.send(player,"<gold>You found a Sunflower Token in the wheat! <gray>It is safe in your discovery pouch. Spend it with Flora. <yellow>/quest discoveries");
        player.playSound(player.getLocation(),Sound.ENTITY_EXPERIENCE_ORB_PICKUP,.7f,1.3f);
        notifyNew(player);
    }
    public void discoveries(Player player){
        var data=plugin.questManager().data(player);long wheat=data.wheatHarvested();
        plugin.send(player,"<gold><bold>Field discoveries</bold>\n<yellow>Sunflower Tokens: <white>"+data.sunflowers()+
                "\n<gray>Next token: <white>"+(750-wheat%750)+" <gray>successful wheat harvests away.\n<gray>Flora accepts these tokens. Ordinary sunflowers do not count.");
        for(var entry:Map.of(750L,"The Sun in the Straw",3000L,"A Courier's Lost Button",10000L,"The Old Field Marker").entrySet().stream().sorted(Map.Entry.comparingByKey()).toList())
            plugin.send(player,(wheat>=entry.getKey()?"<green>Discovered: ":"<dark_gray>Unfound: ")+entry.getValue()+" <gray>("+entry.getKey()+" wheat)");
    }
    private final class Mailbox implements LockedMenu {
        private final Player player;private final Inventory inventory;private final List<Letter> visible;private final int page;
        Mailbox(Player player,int page){
            this.player=player;var data=plugin.questManager().data(player);
            visible=letters.stream().filter(l->l.eligible(data)).sorted(Comparator.comparing(l->data.letterRead(l.id()))).toList();
            this.page=Math.max(0,Math.min(page,Math.max(0,(visible.size()-1)/45)));
            inventory=Bukkit.createInventory(this,54,Text.mm("<dark_gray>Your letters • "+(this.page+1)));
            for(int i=0;i<45&&this.page*45+i<visible.size();i++){
                var l=visible.get(this.page*45+i);boolean read=data.letterRead(l.id());
                inventory.setItem(i,QuestMenu.item(read?Material.PAPER:Material.WRITABLE_BOOK,"<gold>"+Text.escape(l.subject()),
                        List.of("<gray>From "+Text.escape(l.sender()),read?"<gray>Read • click to reread":"<yellow>Unopened • click to read")));
            }
            if(visible.isEmpty())inventory.setItem(22,QuestMenu.item(Material.FEATHER,"<gray>No letters yet",List.of("<gray>Get to know the villagers and work the fields.")));
            if(this.page>0)inventory.setItem(45,QuestMenu.item(Material.ARROW,"<yellow>Previous",List.of()));
            inventory.setItem(49,QuestMenu.item(Material.SUNFLOWER,"<gold>Sunflower Tokens: "+data.sunflowers(),List.of("<gray>Safely banked • spend at Flora's store.","<gray>One token per 750 successful wheat harvests.")));
            if((this.page+1)*45<visible.size())inventory.setItem(53,QuestMenu.item(Material.ARROW,"<yellow>Next",List.of()));
        }
        void open(){player.openInventory(inventory);}
        public UUID viewer(){return player.getUniqueId();}public Inventory getInventory(){return inventory;}
        public void click(int slot,ClickType type){
            if(slot==45&&page>0){new Mailbox(player,page-1).open();return;}
            if(slot==53&&(page+1)*45<visible.size()){new Mailbox(player,page+1).open();return;}
            if(slot==49){player.closeInventory();discoveries(player);return;}
            if(slot<0||slot>=45||page*45+slot>=visible.size())return;
            var letter=visible.get(page*45+slot);var data=plugin.questManager().data(player);
            if(!letters.contains(letter)||!letter.eligible(data)){player.closeInventory();return;}
            var pages=new ArrayList<net.kyori.adventure.text.Component>();
            for(var paragraph:letter.body()){
                String value=paragraph.replace("{player}",Text.escape(player.getName()));
                for(var lines:com.cquests.dialogue.DialogueView.paginate(List.of(value),24,11))
                    pages.add(Text.mm("<black>"+Text.escape(String.join("\n",lines))));
            }
            if(pages.isEmpty())pages.add(Text.mm("<black>The rest of the page is blank."));
            player.closeInventory();
            player.openBook(net.kyori.adventure.inventory.Book.book(Text.mm(Text.escape(letter.subject())),Text.mm(Text.escape(letter.sender())),pages.subList(0,Math.min(100,pages.size()))));
            data.readLetter(letter.id());plugin.store().saveNow(data);notified.remove(player.getUniqueId());
        }
    }
}
