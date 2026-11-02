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
    private volatile Map<String,String> acknowledgements=Map.of();
    private final Map<UUID,Long> notified=new java.util.concurrent.ConcurrentHashMap<>();
    public QuestMail(CQuestsPlugin plugin){this.plugin=plugin;reload();}
    public void reload(){
        var yaml=YamlConfiguration.loadConfiguration(new File(plugin.getDataFolder(),"letters.yml"));
        var root=yaml.getConfigurationSection("letters");var next=new ArrayList<Letter>();var replies=new HashMap<String,String>();
        if(yaml.getBoolean("enabled",true)&&root!=null)for(String id:root.getKeys(false)){
            if(!id.matches("[a-z0-9_-]{1,80}")||next.size()>=512)continue;String p="letters."+id+".";
            replies.put(id,yaml.getString(p+"reply","Your letter is safe with me, {player}. We can speak when you next visit. — {sender}"));
            next.add(new Letter(id,yaml.getString(p+"sender","A friend"),yaml.getString(p+"subject","A letter for you"),
                    yaml.getString(p+"quest",""),yaml.getString(p+"decision",""),yaml.getString(p+"met",""),
                    Math.max(0,yaml.getLong(p+"wheat",0)),yaml.getStringList(p+"body").stream().limit(20).map(s->s.substring(0,Math.min(1600,s.length()))).toList()));
        }letters=List.copyOf(next);acknowledgements=Map.copyOf(replies);
    }
    public void notifyNew(Player player){
        var data=plugin.questManager().data(player);receive(player);long unread=letters.stream().filter(l->l.eligible(data)&&!data.letterRead(l.id())).count();
        Long old=notified.put(player.getUniqueId(),unread);
        if(unread>0&&(old==null||unread>old))plugin.send(player,"<yellow>You have "+unread+" unread letter"+(unread==1?"":"s")+". <white>/quest mail");
    }
    public void forget(Player player){notified.remove(player.getUniqueId());}
    public void open(Player player){receive(player);new Mailbox(player,0).open();}
    private void receive(Player player){var data=plugin.questManager().data(player);for(var l:letters)if(l.eligible(data))data.receiveMail(l.id(),System.currentTimeMillis());if(data.dirty())plugin.store().saveNow(data);}
    public static String time(long epoch){return epoch<=0?"Delivery time unavailable":java.time.format.DateTimeFormatter.ofPattern("dd MMM yyyy HH:mm 'UTC'",Locale.ENGLISH).withZone(java.time.ZoneOffset.UTC).format(java.time.Instant.ofEpochMilli(epoch));}
    private Letter find(Player p,String id){return letters.stream().filter(l->l.id().equals(id)&&l.eligible(plugin.questManager().data(p))).findFirst().orElse(null);}
    public void command(Player player,String[] args){
        if(args.length<2){open(player);return;}
        if(args[1].equalsIgnoreCase("replies")){new ThreadMenu(player).open();return;}
        if(args.length<3){open(player);return;}var letter=find(player,args[2]);
        if(args[1].equalsIgnoreCase("bookthread")){try{var entry=plugin.questManager().data(player).mailThread().get(Integer.parseInt(args[2]));letter=find(player,entry.source());if(letter!=null)book(player,letter,List.of(entry.text()),entry.sender(),entry.time(),false);}catch(RuntimeException ignored){}return;}
        if(letter==null){plugin.send(player,"<gray>This letter is not available in your journey.");return;}
        receive(player);
        switch(args[1].toLowerCase(Locale.ROOT)){
            case "open"->show(player,letter,letter.body(),letter.sender(),plugin.questManager().data(player).mailReceived(letter.id()),"/quest mail book "+letter.id());
            case "book"->book(player,letter,letter.body(),letter.sender(),plugin.questManager().data(player).mailReceived(letter.id()),true);
            case "compose"->compose(player,letter);
            case "send"->{if(args.length>=4)reply(player,letter,String.join(" ",Arrays.copyOfRange(args,3,args.length)));}
            default->open(player);
        }
    }
    private void show(Player player,Letter l,List<String> body,String sender,long sent,String bookCommand){
        player.closeInventory();var lines=new ArrayList<String>();lines.add("<gold>From <white>"+Text.escape(sender)+" <gray>• "+time(sent));
        for(String text:body)lines.add("<white>"+Text.escape(text.replace("{player}",player.getName())));
        var buttons=List.of(new com.cquests.dialogue.MailDialog.Button("Read as a book",bookCommand),new com.cquests.dialogue.MailDialog.Button("Write a reply","/quest mail compose "+l.id()),new com.cquests.dialogue.MailDialog.Button("Back to mailbox","/quest mail"));
        if(!com.cquests.dialogue.MailDialog.open(plugin,player,l.subject(),lines,buttons,false))book(player,l,body,sender,sent,true);
        else{var data=plugin.questManager().data(player);data.readLetter(l.id());plugin.store().saveNow(data);notified.remove(player.getUniqueId());}
    }
    private void compose(Player player,Letter letter){
        var body=List.of("<gold>To <white>"+Text.escape(letter.sender()),"<gray>Your reply stays in your private correspondence.",isBob(letter)?"<gray>B.O.B's replies use Gemini when configured. Your letter and quest memories are sent to Google.":"<gray>This villager will send an authored acknowledgement.");
        if(!com.cquests.dialogue.MailDialog.open(plugin,player,"Write your letter",body,List.of(new com.cquests.dialogue.MailDialog.Button("Send letter","/quest mail send "+letter.id()+" $(message)"),new com.cquests.dialogue.MailDialog.Button("Back","/quest mail open "+letter.id())),true))
            player.sendMessage(net.kyori.adventure.text.Component.text("Write your reply in chat: /quest mail send "+letter.id()+" <message>").clickEvent(net.kyori.adventure.text.event.ClickEvent.suggestCommand("/quest mail send "+letter.id()+" ")));
    }
    private static boolean isBob(Letter l){return l.sender().replaceAll("[^A-Za-z]","").equalsIgnoreCase("bob");}
    private void reply(Player player,Letter letter,String text){
        String clean=text.replaceAll("[\\p{Cntrl}]","").strip();
        if(clean.isBlank()||clean.length()>800){plugin.send(player,"<gray>Write a letter of 1–800 characters.");return;}
        if(isBob(letter)){plugin.gemini().reply(player,letter,clean);return;}
        var data=plugin.questManager().data(player);long now=System.currentTimeMillis();
        if(!data.reserveCorrespondence(now)){plugin.send(player,"<gray>Give the courier a moment before sending another letter.");return;}
        data.addMail(new com.cquests.data.MailEntry(letter.id(),player.getName(),clean,now,true));
        String answer=acknowledgements.getOrDefault(letter.id(),"Your letter made it safely, {player}. — {sender}").replace("{player}",player.getName()).replace("{sender}",letter.sender());
        data.addMail(new com.cquests.data.MailEntry(letter.id(),letter.sender(),answer,now,false));plugin.store().saveNow(data);plugin.send(player,"<gold>"+Text.escape(letter.sender())+" has answered. <white>/quest mail replies");
    }
    private void book(Player player,Letter letter,List<String> body,String sender,long sent,boolean markRead){
        var pages=new ArrayList<net.kyori.adventure.text.Component>();
        pages.add(net.kyori.adventure.text.Component.text("From: "+sender+"\nDelivered: "+time(sent)+"\n\n"+letter.subject(),net.kyori.adventure.text.format.NamedTextColor.BLACK));
        for(String paragraph:body)for(var lines:com.cquests.dialogue.DialogueView.paginate(List.of(Text.escape(paragraph.replace("{player}",player.getName()))),18,8))pages.add(Text.mm("<black>"+Text.escape(String.join("\n",lines))));
        pages.add(net.kyori.adventure.text.Component.text("Write a reply",net.kyori.adventure.text.format.NamedTextColor.DARK_GREEN).clickEvent(net.kyori.adventure.text.event.ClickEvent.runCommand("/quest mail compose "+letter.id())));
        player.closeInventory();player.openBook(net.kyori.adventure.inventory.Book.book(net.kyori.adventure.text.Component.text(letter.subject()),net.kyori.adventure.text.Component.text(sender),pages.subList(0,Math.min(100,pages.size()))));
        if(markRead){var data=plugin.questManager().data(player);data.readLetter(letter.id());plugin.store().saveNow(data);notified.remove(player.getUniqueId());}
    }
    private final class ThreadMenu implements LockedMenu {
        final Player player;final Inventory inventory;final List<com.cquests.data.MailEntry> entries;
        ThreadMenu(Player p){player=p;var copy=new ArrayList<>(plugin.questManager().data(p).mailThread());Collections.reverse(copy);entries=List.copyOf(copy);inventory=Bukkit.createInventory(this,45,Text.mm("<dark_gray>Your correspondence"));
            for(int i=0;i<entries.size();i++){var e=entries.get(i);inventory.setItem(i,QuestMenu.item(Material.WRITABLE_BOOK,"<gold>"+Text.escape(e.sender()),List.of("<gray>"+time(e.time()),"<gray>"+Text.escape(e.text().substring(0,Math.min(80,e.text().length()))),"<yellow>Click to read and reply.")));}
            inventory.setItem(44,QuestMenu.item(Material.ARROW,"<yellow>Mailbox",List.of()));
        }
        void open(){player.openInventory(inventory);}public UUID viewer(){return player.getUniqueId();}public Inventory getInventory(){return inventory;}
        public void click(int slot,ClickType type){if(slot==44){QuestMail.this.open(player);return;}if(slot<0||slot>=entries.size())return;var entry=entries.get(slot);var l=find(player,entry.source());var saved=plugin.questManager().data(player).mailThread();int index=saved.indexOf(entry);if(l!=null&&index>=0)show(player,l,List.of(entry.text()),entry.sender(),entry.time(),"/quest mail bookthread "+index);}
    }
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
                        List.of("<gray>From "+Text.escape(l.sender()),"<gray>Delivered "+time(data.mailReceived(l.id())),read?"<gray>Read • click to reread":"<yellow>Unopened • click to read")));
            }
            inventory.setItem(50,QuestMenu.item(Material.WRITABLE_BOOK,"<gold>Replies and conversations",List.of("<gray>Read your correspondence.")));
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
            if(slot==50){new ThreadMenu(player).open();return;}
            if(slot==49){player.closeInventory();discoveries(player);return;}
            if(slot<0||slot>=45||page*45+slot>=visible.size())return;
            var letter=visible.get(page*45+slot);var data=plugin.questManager().data(player);
            if(!letters.contains(letter)||!letter.eligible(data)){player.closeInventory();return;}
            show(player,letter,letter.body(),letter.sender(),data.mailReceived(letter.id()),"/quest mail book "+letter.id());

        }
    }
}
