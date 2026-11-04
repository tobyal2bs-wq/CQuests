package com.cquests.gui;

import com.cquests.T;

import com.cquests.CQuestsPlugin;
import com.cquests.dialogue.DialogueView;
import com.cquests.dialogue.MailDialog;
import com.cquests.model.Quest;
import com.cquests.util.Text;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.entity.Player;
import org.bukkit.event.inventory.ClickType;
import org.bukkit.inventory.Inventory;
import java.util.*;

/** A small home screen and explicit back paths; reading it never accepts or completes a quest. */
public final class QuestJournal {
    private static final String HOME="/quests journal";
    private QuestJournal() {}
    private static MailDialog.Button button(String text,String command){return new MailDialog.Button(text,command);}
    private static MailDialog.Button back(){return button("Back to quest home",HOME);}
    private static String plain(String text){return Text.plain(Text.mm(text==null?"":text));}
    private static String name(CQuestsPlugin plugin,Player player,Quest quest){return plain(plugin.questManager().fill(quest.name(),player));}
    private static int number(String[] args,int index){try{return Math.max(0,Integer.parseInt(args[index]));}catch(RuntimeException ignored){return 0;}}

    public static void open(CQuestsPlugin plugin,Player player){command(plugin,player,new String[]{"journal"});}
    public static void command(CQuestsPlugin plugin,Player player,String[] args){
        if(!player.hasPermission("quests.use")){plugin.send(player,T.t("quest-journal.you-need-quests-use-to", "<red>You need quests.use to open your quests."));return;}
        String action=args.length>1?args[1].toLowerCase(Locale.ROOT):"home";
        switch(action){
            case "close"->player.closeInventory();
            case "quests"->list(plugin,player,number(args,2));
            case "story"->{var q=plugin.questManager().nextStoryQuest(plugin.questManager().data(player));if(q==null)home(plugin,player);else detail(plugin,player,q,0);}
            case "quest","guide"->{
                var data=plugin.questManager().data(player);var q=args.length>2?plugin.quests().get(args[2]):null;
                var next=plugin.questManager().nextStoryQuest(data);
                if(q==null||(!data.isActive(q.id())&&(next==null||!next.id().equals(q.id())))){home(plugin,player);return;}
                if(action.equals("guide")&&data.isActive(q.id())){
                    plugin.tracker().track(player,q.id());
                    if(!plugin.directions().enabled(player))plugin.directions().toggle(player);else plugin.directions().update(player);
                }
                detail(plugin,player,q,number(args,3));
            }
            case "settings"->settings(plugin,player);
            case "tracker"->{plugin.tracker().toggle(player);settings(plugin,player);}
            case "directions"->{plugin.directions().toggle(player);settings(plugin,player);}
            default->home(plugin,player);
        }
    }
    private static void home(CQuestsPlugin plugin,Player player){
        var data=plugin.questManager().data(player);var next=plugin.questManager().nextStoryQuest(data);
        var active=plugin.questManager().activeQuests(data);var lines=new ArrayList<String>();
        lines.add("<gold>Wayfarer level <white>"+plugin.progression().level(data));
        if(next==null)lines.add("<green>Your main story is complete. There is still work in the fields and with the villagers.");
        else lines.add("<white>Next story quest: <yellow>"+Text.escape(name(plugin,player,next))+"\n<gray>Choose What should I do? for your next step.");
        var buttons=new ArrayList<MailDialog.Button>();
        if(next!=null)buttons.add(button("What should I do?",HOME+" story"));
        buttons.add(button("My quests ("+active.size()+")",HOME+" quests"));
        buttons.add(button("Quest settings",HOME+" settings"));buttons.add(button("Close",HOME+" close"));
        screen(plugin,player,"Quest home",lines,buttons);
    }
    private static void list(CQuestsPlugin plugin,Player player,int requested){
        var active=plugin.questManager().activeQuests(plugin.questManager().data(player));
        int page=Math.min(requested,Math.max(0,(active.size()-1)/5));var buttons=new ArrayList<MailDialog.Button>();
        for(var q:active.subList(page*5,Math.min(active.size(),page*5+5)))buttons.add(button(name(plugin,player,q),HOME+" quest "+q.id()));
        if(page>0)buttons.add(button("Previous quests",HOME+" quests "+(page-1)));
        if((page+1)*5<active.size())buttons.add(button("More quests",HOME+" quests "+(page+1)));
        buttons.add(back());
        screen(plugin,player,"My quests",List.of(active.isEmpty()?"<white>No active quests. Start with What should I do? on Quest home.":"<white>Choose a quest to see exactly what to do.","<gray>Page "+(page+1)+" of "+Math.max(1,(active.size()+4)/5)),buttons);
    }
    private static void detail(CQuestsPlugin plugin,Player player,Quest quest,int requested){
        var qm=plugin.questManager();var data=qm.data(player);var active=data.active(quest.id());var text=new ArrayList<String>();
        if(active==null){
            if(!plugin.progression().canTake(data,quest.level()))text.add("Reach Wayfarer level "+Math.max(1,quest.level())+" first. You are level "+plugin.progression().level(data)+". Harvest wheat and finish available jobs to earn XP.");
            String gate=qm.chapterGate(data,quest);
            if(gate!=null)text.add("Help "+plain(plugin.npcs().name(gate))+" with their remaining jobs first.");
            if(!qm.requirementsMet(data,quest)&&gate==null&&plugin.progression().canTake(data,quest.level()))text.add("Finish your previous story tasks first.");
            if(qm.requirementsMet(data,quest))text.add(quest.giver().isEmpty()?"Speak to the villagers at spawn to start this task.":"Speak to "+plain(plugin.npcs().name(quest.giver()))+" to start this quest.");
        }else if(qm.ready(quest,active)){
            text.add(quest.turnIn().isEmpty()?"All tasks are done. Your quest will finish automatically.":"All tasks are done! Return to "+plain(plugin.npcs().name(quest.turnIn()))+" and speak to them to collect your reward.");
        }else{
            boolean first=true;
            for(int i=0;i<quest.objectives().size();i++){
                var objective=quest.objectives().get(i);boolean done=qm.objectiveDone(quest,active,i);
                String progress=objective.amount()>1?" ("+Math.min(active.get(i),objective.amount())+"/"+objective.amount()+")":"";
                text.add((done?"Done: ":first?"Next: ":"Then: ")+plain(qm.objectiveLabel(objective))+progress);
                if(!done)first=false;
            }
        }
        var pages=DialogueView.paginate(text.stream().map(Text::escape).toList(),52,8);int page=Math.min(requested,pages.size()-1);
        var lines=new ArrayList<String>();lines.add("<white>"+Text.escape(String.join("\n",pages.get(page))));
        if(pages.size()>1)lines.add("<gray>Page "+(page+1)+" of "+pages.size());
        if(active!=null&&quest.id().equals(plugin.tracker().tracked(player))&&plugin.directions().enabled(player))lines.add("<gray>Follow the arrow and distance after closing this screen.");
        var buttons=new ArrayList<MailDialog.Button>();
        if(page>0)buttons.add(button("Previous page",HOME+" quest "+quest.id()+" "+(page-1)));
        if(page+1<pages.size())buttons.add(button("Next page",HOME+" quest "+quest.id()+" "+(page+1)));
        if(active!=null)buttons.add(button("Show directions",HOME+" guide "+quest.id()));
        buttons.add(button("Back to my quests",HOME+" quests"));buttons.add(back());
        screen(plugin,player,name(plugin,player,quest),lines,buttons);
    }
    private static void settings(CQuestsPlugin plugin,Player player){
        screen(plugin,player,"Quest settings",List.of("<white>Choose what appears while you play.","<gray>Quest tracker: a bar showing your current task.\nDirections: an arrow and distance to the villager."),List.of(
                button("Quest tracker: "+(plugin.tracker().enabled(player)?"ON":"OFF"),HOME+" tracker"),
                button("Directions: "+(plugin.directions().enabled(player)?"ON":"OFF"),HOME+" directions"),back()));
    }
    private static void screen(CQuestsPlugin plugin,Player player,String title,List<String> lines,List<MailDialog.Button> buttons){
        player.closeInventory();if(!MailDialog.open(plugin,player,title,lines,buttons,false))new Fallback(plugin,player,title,lines,buttons).open();
    }
    private static final class Fallback implements LockedMenu {
        private final CQuestsPlugin plugin;private final Player player;private final Inventory inventory;private final List<MailDialog.Button> buttons;
        Fallback(CQuestsPlugin plugin,Player player,String title,List<String> lines,List<MailDialog.Button> buttons){
            this.plugin=plugin;this.player=player;this.buttons=List.copyOf(buttons);inventory=Bukkit.createInventory(this,54,Text.mm("<dark_gray>"+Text.escape(title)));
            inventory.setItem(13,QuestMenu.item(Material.MAP,"<gold>"+Text.escape(title),lines));
            for(int i=0;i<buttons.size();i++)inventory.setItem(27+i,QuestMenu.item(Material.ARROW,"<white>"+Text.escape(buttons.get(i).label()),List.of("<yellow>Click to open.")));
        }
        void open(){player.openInventory(inventory);}public UUID viewer(){return player.getUniqueId();}public Inventory getInventory(){return inventory;}
        public void click(int slot,ClickType type){int i=slot-27;if(i<0||i>=buttons.size())return;String command=buttons.get(i).command();if(command.startsWith(HOME))QuestJournal.command(plugin,player,command.substring("/quests ".length()).split(" "));else player.performCommand(command.substring(1));}
    }
}
