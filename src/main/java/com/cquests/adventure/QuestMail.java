package com.cquests.adventure;

import com.cquests.T;

import com.cquests.CQuestsPlugin;
import com.cquests.data.PlayerData;
import com.cquests.dialogue.MailDialog;
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
        if(unread>0&&(old==null||unread>old))plugin.send(player,T.t("quest-mail.you-have-unread-letter-quest", "<yellow>You have <unread> unread letter<s>. <white>/quest mail", "unread", unread, "s", (unread==1?"":"s")));
    }
    public void forget(Player player){notified.remove(player.getUniqueId());}
    public void open(Player player){inbox(player,0);}
    private static int number(String[] args,int index){try{return Math.max(0,Integer.parseInt(args[index]));}catch(RuntimeException ignored){return 0;}}
    private List<Letter> visible(PlayerData data){return letters.stream().filter(l->l.eligible(data)).sorted(Comparator.comparing(l->data.letterRead(l.id()))).toList();}
    private void inbox(Player player,int requested){
        receive(player);var data=plugin.questManager().data(player);var available=visible(data);
        int page=Math.min(requested,Math.max(0,(available.size()-1)/5));
        long unread=available.stream().filter(l->!data.letterRead(l.id())).count();
        var lines=new ArrayList<String>();lines.add("<white>Letters from the villagers you've met.");
        lines.add(available.isEmpty()?"<gray>No letters yet. Meet the villagers and help them out.":"<yellow>"+unread+" unread <gray>• Choose a letter below.");
        if(available.size()>5)lines.add("<gray>Page "+(page+1)+" of "+((available.size()+4)/5));
        var buttons=new ArrayList<MailDialog.Button>();
        for(var l:available.subList(page*5,Math.min(available.size(),page*5+5)))
            buttons.add(new MailDialog.Button((data.letterRead(l.id())?"":"NEW • ")+who(l.sender())+" — "+l.subject(),"/quest mail open "+l.id()));
        if(page>0)buttons.add(new MailDialog.Button("Previous letters","/quest mail inbox "+(page-1)));
        if((page+1)*5<available.size())buttons.add(new MailDialog.Button("More letters","/quest mail inbox "+(page+1)));
        if(!data.mailThread().isEmpty())buttons.add(new MailDialog.Button("Sent letters & replies","/quest mail replies"));
        buttons.add(new MailDialog.Button("Close","/quest mail close"));
        player.closeInventory();
        if(!MailDialog.open(plugin,player,"Your mail",lines,buttons,false))new Mailbox(player,page/9).open();
    }
    private void receive(Player player){var data=plugin.questManager().data(player);boolean changed=false;long now=System.currentTimeMillis();for(var l:letters)if(l.eligible(data)&&data.mailReceived(l.id())==0)changed|=data.receiveMail(l.id(),now)>0;if(changed)plugin.store().saveNow(data);}
    public static String time(long epoch){return epoch<=0?"Delivery time unavailable":java.time.format.DateTimeFormatter.ofPattern("dd MMM yyyy HH:mm 'UTC'",Locale.ENGLISH).withZone(java.time.ZoneOffset.UTC).format(java.time.Instant.ofEpochMilli(epoch));}
    private Letter find(Player p,String id){return letters.stream().filter(l->l.id().equals(id)&&l.eligible(plugin.questManager().data(p))).findFirst().orElse(null);}
    public void command(Player player,String[] args){
        if(args.length<2){open(player);return;}
        if(args[1].equalsIgnoreCase("close")){player.closeInventory();return;}
        if(args[1].equalsIgnoreCase("inbox")){inbox(player,number(args,2));return;}
        if(args[1].equalsIgnoreCase("replies")){history(player,number(args,2));return;}
        if(args[1].equalsIgnoreCase("thread")){thread(player,number(args,2),number(args,3));return;}
        if(args.length<3){open(player);return;}var letter=find(player,args[2]);
        if(args[1].equalsIgnoreCase("bookthread")){try{var entry=plugin.questManager().data(player).mailThread().get(Integer.parseInt(args[2]));letter=find(player,entry.source());if(letter!=null)book(player,letter,List.of(entry.text()),who(entry.sender()),entry.time(),false);}catch(RuntimeException ignored){}return;}
        if(letter==null){plugin.send(player,T.t("quest-mail.this-letter-is-not-available", "<gray>This letter is not available in your journey."));return;}
        receive(player);
        switch(args[1].toLowerCase(Locale.ROOT)){
            case "open"->show(player,letter,letter.body(),who(letter.sender()),plugin.questManager().data(player).mailReceived(letter.id()),"/quest mail open "+letter.id(),number(args,3));
            case "book"->book(player,letter,letter.body(),who(letter.sender()),plugin.questManager().data(player).mailReceived(letter.id()),true);
            case "compose"->compose(player,letter);
            case "send"->{if(args.length>=4)reply(player,letter,String.join(" ",Arrays.copyOfRange(args,3,args.length)));}
            default->open(player);
        }
    }
    private void show(Player player,Letter l,List<String> body,String sender,long sent,String route,int requested){
        player.closeInventory();var pages=com.cquests.dialogue.DialogueView.paginate(body.stream().map(t->Text.escape(t.replace("{player}",player.getName()))).toList(),52,8);
        int page=Math.min(requested,pages.size()-1);var lines=new ArrayList<String>();
        lines.add("<gold>From <white>"+Text.escape(sender)+"\n<gray>"+time(sent));
        lines.add("<white>"+Text.escape(String.join("\n",pages.get(page))));
        if(pages.size()>1)lines.add("<gray>Page "+(page+1)+" of "+pages.size());
        var buttons=new ArrayList<MailDialog.Button>();
        if(page>0)buttons.add(new MailDialog.Button("Previous page",route+" "+(page-1)));
        if(page+1<pages.size())buttons.add(new MailDialog.Button("Next page",route+" "+(page+1)));
        if(!isBob(l)||plugin.gemini().unavailable()==null)buttons.add(new MailDialog.Button("Reply to "+who(l.sender()),"/quest mail compose "+l.id()));
        else lines.add("<gray>"+Text.escape(who("bob"))+" isn't receiving replies yet. You can still read his letters.");
        if(plugin.questManager().data(player).mailThread().stream().anyMatch(e->e.source().equals(l.id())))buttons.add(new MailDialog.Button("Sent letters & replies","/quest mail replies"));
        buttons.add(new MailDialog.Button("Back to inbox","/quest mail"));
        if(!MailDialog.open(plugin,player,l.subject(),lines,buttons,false))new ReadingMenu(player,l.subject(),lines,buttons).open();
        var data=plugin.questManager().data(player);if(data.readLetter(l.id()))plugin.store().saveNow(data);notified.remove(player.getUniqueId());
    }
    private void compose(Player player,Letter letter){
        if(isBob(letter)&&plugin.gemini().unavailable()!=null){show(player,letter,letter.body(),who(letter.sender()),plugin.questManager().data(player).mailReceived(letter.id()),"/quest mail open "+letter.id(),0);return;}
        var body=new ArrayList<String>();body.add("<gold>To <white>"+Text.escape(who(letter.sender())));body.add("<gray>"+Text.escape(letter.subject()));body.add("<white>Type your message below, then press Send.");
        if(isBob(letter))body.add("<gray>"+Text.escape(who("bob"))+" uses AI. Your message, this conversation and quest memories will be sent to Google.");
        player.closeInventory();if(!MailDialog.open(plugin,player,"Reply to "+who(letter.sender()),body,List.of(new MailDialog.Button("Send","/quest mail send "+letter.id()+" $(message)"),new MailDialog.Button("Back to letter","/quest mail open "+letter.id())),true))
            player.sendMessage(net.kyori.adventure.text.Component.text("Write your reply in chat: /quest mail send "+letter.id()+" <message>").clickEvent(net.kyori.adventure.text.event.ClickEvent.suggestCommand("/quest mail send "+letter.id()+" ")));
    }
    private String floraName(){return Text.escape(who("flora"));}
    private boolean isBob(Letter l){
        var npcs=plugin.npcs();
        return npcs==null?l.sender().replaceAll("[^A-Za-z]","").equalsIgnoreCase("bob"):"bob".equals(npcs.idForOriginalName(l.sender()));
    }
    /** The sender's current name, so renaming an NPC or merchant (/cq npc rename) also renames their letters. */
    private String who(String sender){
        var npcs=plugin.npcs();var characters=plugin.characters();
        String id=npcs==null?null:npcs.idForOriginalName(sender);
        if(id!=null)return npcs.name(id);
        if(characters==null)return sender;
        String key=sender.toLowerCase(java.util.Locale.ROOT);
        var merchant=plugin.merchants()==null?null:plugin.merchants().get(key);
        if(merchant!=null)return Text.plain(Text.mm(characters.text(key,"name",merchant.name())));
        if(key.equals("pip"))return Text.plain(Text.mm(characters.text("pip","name",sender)));
        return sender;
    }
    private void reply(Player player,Letter letter,String text){
        String clean=text.replaceAll("[\\p{Cntrl}]","").strip();
        if(clean.isBlank()||clean.length()>800){plugin.send(player,T.t("quest-mail.write-a-letter-of-1", "<gray>Write a letter of 1–800 characters."));return;}
        if(isBob(letter)){plugin.gemini().reply(player,letter,clean);return;}
        var data=plugin.questManager().data(player);long now=System.currentTimeMillis();
        if(!data.reserveCorrespondence(now)){plugin.send(player,T.t("quest-mail.give-the-courier-a-moment", "<gray>Give the courier a moment before sending another letter."));return;}
        data.addMail(new com.cquests.data.MailEntry(letter.id(),player.getName(),clean,now,true));
        String answer=acknowledgements.getOrDefault(letter.id(),"Your letter made it safely, {player}. — {sender}").replace("{player}",player.getName()).replace("{sender}",who(letter.sender()));
        data.addMail(new com.cquests.data.MailEntry(letter.id(),letter.sender(),answer,now,false));plugin.store().saveNow(data);plugin.send(player,T.t("quest-mail.has-answered-quest-mail-replies", "<gold><sender> has answered. <white>/quest mail replies", "sender", Text.escape(who(letter.sender()))));
        thread(player,data.mailThread().size()-1,0);
    }
    private void history(Player player,int requested){
        var entries=plugin.questManager().data(player).mailThread();int page=Math.min(requested,Math.max(0,(entries.size()-1)/5));
        var lines=new ArrayList<String>();lines.add(entries.isEmpty()?"<gray>No replies yet. Open a letter in your inbox and choose Reply.":"<white>Your sent letters and the villagers' answers.");
        if(entries.size()>5)lines.add("<gray>Page "+(page+1)+" of "+((entries.size()+4)/5));
        var buttons=new ArrayList<MailDialog.Button>();
        for(int i=entries.size()-1-page*5;i>=Math.max(0,entries.size()-5-page*5);i--){var e=entries.get(i);var l=find(player,e.source());if(l!=null)buttons.add(new MailDialog.Button((e.fromPlayer()?"To "+who(l.sender()):"From "+who(e.sender()))+" • "+time(e.time()),"/quest mail thread "+i));}
        if(page>0)buttons.add(new MailDialog.Button("Newer messages","/quest mail replies "+(page-1)));
        if((page+1)*5<entries.size())buttons.add(new MailDialog.Button("Older messages","/quest mail replies "+(page+1)));
        buttons.add(new MailDialog.Button("Back to inbox","/quest mail"));player.closeInventory();
        if(!MailDialog.open(plugin,player,"Sent letters & replies",lines,buttons,false))new ThreadMenu(player).open();
    }
    private void thread(Player player,int index,int page){
        var entries=plugin.questManager().data(player).mailThread();if(index>=entries.size()){history(player,0);return;}
        var entry=entries.get(index);var letter=find(player,entry.source());
        if(letter==null){history(player,0);return;}
        show(player,letter,List.of(entry.text()),entry.fromPlayer()?"You → "+who(letter.sender()):who(entry.sender()),entry.time(),"/quest mail thread "+index,page);
    }
    private void book(Player player,Letter letter,List<String> body,String sender,long sent,boolean markRead){
        var pages=new ArrayList<net.kyori.adventure.text.Component>();
        pages.add(net.kyori.adventure.text.Component.text("From: "+sender+"\nDelivered: "+time(sent)+"\n\n"+letter.subject(),net.kyori.adventure.text.format.NamedTextColor.BLACK));
        for(String paragraph:body)for(var lines:com.cquests.dialogue.DialogueView.paginate(List.of(Text.escape(paragraph.replace("{player}",player.getName()))),18,8))pages.add(Text.mm("<black>"+Text.escape(String.join("\n",lines))));
        pages.add(net.kyori.adventure.text.Component.text("Write a reply",net.kyori.adventure.text.format.NamedTextColor.DARK_GREEN).clickEvent(net.kyori.adventure.text.event.ClickEvent.runCommand("/quest mail compose "+letter.id())));
        player.closeInventory();player.openBook(net.kyori.adventure.inventory.Book.book(net.kyori.adventure.text.Component.text(letter.subject()),net.kyori.adventure.text.Component.text(sender),pages.subList(0,Math.min(100,pages.size()))));
        if(markRead){var data=plugin.questManager().data(player);if(data.readLetter(letter.id()))plugin.store().saveNow(data);notified.remove(player.getUniqueId());}
    }
    private final class ThreadMenu implements LockedMenu {
        final Player player;final Inventory inventory;final List<com.cquests.data.MailEntry> entries;
        ThreadMenu(Player p){player=p;var copy=new ArrayList<>(plugin.questManager().data(p).mailThread());Collections.reverse(copy);entries=List.copyOf(copy);inventory=Bukkit.createInventory(this,45,Text.mm(T.t("quest-mail.your-correspondence", "<dark_gray>Your correspondence")));
            for(int i=0;i<entries.size();i++){var e=entries.get(i);inventory.setItem(i,QuestMenu.item(Material.WRITABLE_BOOK,"<gold>"+Text.escape(who(e.sender())),List.of("<gray>"+time(e.time()),"<gray>"+Text.escape(e.text().substring(0,Math.min(80,e.text().length()))),"<yellow>Click to read and reply.")));}
            inventory.setItem(44,QuestMenu.item(Material.ARROW,"<yellow>Mailbox",List.of()));
        }
        void open(){player.openInventory(inventory);}public UUID viewer(){return player.getUniqueId();}public Inventory getInventory(){return inventory;}
        public void click(int slot,ClickType type){if(slot==44){QuestMail.this.open(player);return;}if(slot<0||slot>=entries.size())return;var entry=entries.get(slot);var saved=plugin.questManager().data(player).mailThread();int index=saved.indexOf(entry);if(index>=0)thread(player,index,0);}
    }
    /** Older clients keep a locked, readable menu; mail never requires opening a book. */
    private final class ReadingMenu implements LockedMenu {
        final Player player;final Inventory inventory;final List<MailDialog.Button> buttons;
        ReadingMenu(Player player,String title,List<String> lines,List<MailDialog.Button> buttons){
            this.player=player;this.buttons=List.copyOf(buttons);inventory=Bukkit.createInventory(this,54,Text.mm(T.t("quest-mail.mail", "<dark_gray>Mail")));
            inventory.setItem(13,QuestMenu.item(Material.PAPER,"<gold>"+Text.escape(title),lines));
            inventory.setItem(4,QuestMenu.item(Material.FEATHER,"<yellow>Hover over the letter to read",List.of("<gray>Use the buttons below to continue.")));
            for(int i=0;i<buttons.size();i++)inventory.setItem(27+i,QuestMenu.item(Material.ARROW,"<white>"+Text.escape(buttons.get(i).label()),List.of()));
        }
        void open(){player.openInventory(inventory);}public UUID viewer(){return player.getUniqueId();}public Inventory getInventory(){return inventory;}
        public void click(int slot,ClickType type){int index=slot-27;if(index<0||index>=buttons.size())return;String command=buttons.get(index).command();QuestMail.this.command(player,command.substring("/quest ".length()).split(" "));}
    }
    public void discovered(Player player){
        var data=plugin.questManager().data(player);
        if(data.wheatHarvested()%750!=0)return;
        plugin.store().saveNow(data);
        plugin.send(player,T.t("quest-mail.you-found-a-sunflower-token", "<gold>You found a Sunflower Token in the wheat! <gray>It is safe in your discovery pouch. Spend it with <floraname>. <yellow>/quest discoveries", "floraname", floraName()));
        player.playSound(player.getLocation(),Sound.ENTITY_EXPERIENCE_ORB_PICKUP,.7f,1.3f);
        notifyNew(player);
    }
    public void discoveries(Player player){
        var data=plugin.questManager().data(player);long wheat=data.wheatHarvested();
        plugin.send(player,T.t("quest-mail.field-discoveries-sunflower-tokens-next", "<gold><bold>Field discoveries</bold>\n<yellow>Sunflower Tokens: <white><sunflowers>\n<gray>Next token: <white><wheat> <gray>successful wheat harvests away.\n<gray><floraname> accepts these tokens. Ordinary sunflowers do not count.", "sunflowers", data.sunflowers(), "wheat", (750-wheat%750), "floraname", floraName()));
        for(var entry:Map.of(750L,"The Sun in the Straw",3000L,"A Courier's Lost Button",10000L,"The Old Field Marker").entrySet().stream().sorted(Map.Entry.comparingByKey()).toList())
            plugin.send(player,T.t("quest-mail.wheat", "<unfound><getvalue> <gray>(<getkey> wheat)", "unfound", (wheat>=entry.getKey()?"<green>Discovered: ":"<dark_gray>Unfound: "), "getvalue", entry.getValue(), "getkey", entry.getKey()));
    }
    private final class Mailbox implements LockedMenu {
        private final Player player;private final Inventory inventory;private final List<Letter> visible;private final int page;
        Mailbox(Player player,int page){
            this.player=player;var data=plugin.questManager().data(player);
            visible=letters.stream().filter(l->l.eligible(data)).sorted(Comparator.comparing(l->data.letterRead(l.id()))).toList();
            this.page=Math.max(0,Math.min(page,Math.max(0,(visible.size()-1)/45)));
            inventory=Bukkit.createInventory(this,54,Text.mm(T.t("quest-mail.your-letters", "<dark_gray>Your letters • <page>", "page", (this.page+1))));
            for(int i=0;i<45&&this.page*45+i<visible.size();i++){
                var l=visible.get(this.page*45+i);boolean read=data.letterRead(l.id());
                inventory.setItem(i,QuestMenu.item(read?Material.PAPER:Material.WRITABLE_BOOK,"<gold>"+Text.escape(l.subject()),
                        List.of("<gray>From "+Text.escape(who(l.sender())),"<gray>Delivered "+time(data.mailReceived(l.id())),read?"<gray>Read • click to reread":"<yellow>Unopened • click to read")));
            }
            inventory.setItem(50,QuestMenu.item(Material.WRITABLE_BOOK,"<gold>Replies and conversations",List.of("<gray>Read your correspondence.")));
            if(visible.isEmpty())inventory.setItem(22,QuestMenu.item(Material.FEATHER,"<gray>No letters yet",List.of("<gray>Get to know the villagers and work the fields.")));
            if(this.page>0)inventory.setItem(45,QuestMenu.item(Material.ARROW,"<yellow>Previous",List.of()));
            inventory.setItem(49,QuestMenu.item(Material.SUNFLOWER,"<gold>Sunflower Tokens: "+data.sunflowers(),List.of("<gray>Safely banked • spend at "+floraName()+"'s store.","<gray>One token per 750 successful wheat harvests.")));
            if((this.page+1)*45<visible.size())inventory.setItem(53,QuestMenu.item(Material.ARROW,"<yellow>Next",List.of()));
        }
        void open(){player.openInventory(inventory);}
        public UUID viewer(){return player.getUniqueId();}public Inventory getInventory(){return inventory;}
        public void click(int slot,ClickType type){
            if(slot==45&&page>0){new Mailbox(player,page-1).open();return;}
            if(slot==53&&(page+1)*45<visible.size()){new Mailbox(player,page+1).open();return;}
            if(slot==50){history(player,0);return;}
            if(slot==49){player.closeInventory();discoveries(player);return;}
            if(slot<0||slot>=45||page*45+slot>=visible.size())return;
            var letter=visible.get(page*45+slot);var data=plugin.questManager().data(player);
            if(!letters.contains(letter)||!letter.eligible(data)){player.closeInventory();return;}
            show(player,letter,letter.body(),who(letter.sender()),data.mailReceived(letter.id()),"/quest mail open "+letter.id(),0);

        }
    }
}
