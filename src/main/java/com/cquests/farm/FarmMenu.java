package com.cquests.farm;

import com.cquests.T;

import com.cquests.CQuestsPlugin;
import com.cquests.gui.LockedMenu;
import com.cquests.gui.QuestMenu;
import com.cquests.util.Text;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.event.inventory.ClickType;
import org.bukkit.inventory.Inventory;
import java.util.*;

/** Purchases are derived from the authoritative player ledger, never from a lore string or client item. */
public final class FarmMenu implements LockedMenu {
    private final CQuestsPlugin plugin;private final Player player;private final Inventory inventory;private final FarmService.Spot station;
    private final Map<Integer,Integer> choices=new HashMap<>();private Integer confirm;
    private FarmMenu(CQuestsPlugin p,Player player,FarmService.Spot station){plugin=p;this.player=player;this.station=station;inventory=Bukkit.createInventory(this,45,Text.mm(T.t("farm-menu.fieldsmith-hoe-upgrades", "<dark_gray>Fieldsmith • Hoe upgrades")));}
    public static void open(CQuestsPlugin p,Player player){var station=p.farm().nearbyUpgrader(player);if(station==null){p.send(player,"<yellow>Right-click the Fieldsmith Anvil to upgrade your hoe.");return;}var m=new FarmMenu(p,player,station);m.fill();player.openInventory(m.inventory);}
    public UUID viewer(){return player.getUniqueId();}
    public Inventory getInventory(){return inventory;}
    private void fill(){
        choices.clear();confirm=null;
        for(int i=0;i<45;i++)inventory.setItem(i,QuestMenu.item(Material.GRAY_STAINED_GLASS_PANE," ",List.of()));
        var data=plugin.questManager().data(player);
        inventory.setItem(4,QuestMenu.item(Material.ANVIL,"<gold><bold>A little work. A better harvest.",List.of(
                "<white>Wayfarer level "+plugin.progression().level(data),"<gray>Choose an upgrade. Make every harvest count.")));
        var current=plugin.farm().tier(data.hoeTier());
        var next=plugin.farm().tier(data.hoeTier()+1);
        inventory.setItem(20,current==null
                ?QuestMenu.item(Material.WOODEN_HOE,"<white>Your first field tool",List.of("<gray>Collect your starter hoe here."))
                :QuestMenu.item(current.material(),"<gold><bold>"+Text.escape(current.name()),List.of(
                    "<green>YOUR HOE","","<gray>Harvest XP <aqua>×"+current.multiplier(),
                    "<gray>Extra wheat <yellow>"+Math.round(current.chance()*100)+"%")));
        inventory.setItem(22,QuestMenu.item(Material.SMITHING_TABLE,"<gold>Make it count",List.of(
                "<gray>Your hoe on the left.","<gray>Your next upgrade on the right.")));
        if(next==null){
            inventory.setItem(24,QuestMenu.item(Material.NETHER_STAR,"<gold><bold>Finest tool in the fields",List.of(
                    "<gray>No more upgrades. Put it to work!")));
            inventory.setItem(34,QuestMenu.item(Material.LIME_STAINED_GLASS_PANE,"<green>Fully upgraded",List.of()));
        }else{
            inventory.setItem(24,QuestMenu.item(next.material(),"<yellow><bold>"+Text.escape(next.name()),List.of(
                    "<yellow>NEXT UPGRADE","","<gray>Harvest XP <aqua>×"+next.multiplier(),
                    "<gray>Extra wheat <yellow>"+Math.round(next.chance()*100)+"%",
                    "<gray>Time between hits <white>"+next.cooldown()/20.0+"s","",
                    "<gray>Wayfarer level <white>"+next.level(),"<gray>Price <gold>$"+Text.formatMoney(next.cost()),
                    "","<yellow>Click to review this upgrade.")));
            choices.put(24,next.id());
            choices.put(34,next.id());
            boolean eligible=plugin.progression().level(data)>=next.level();
            inventory.setItem(34,QuestMenu.item(eligible?Material.LIME_DYE:Material.RED_TERRACOTTA,
                    eligible?"<green><bold>Review upgrade":"<red>More fieldwork first",List.of(
                    "<gray>"+Text.escape(next.name()),"<gray>Wayfarer level <white>"+next.level(),
                    "<gold>$"+Text.formatMoney(next.cost()),eligible?"<yellow>Click to continue.":"<gray>Harvest wheat and finish jobs to earn XP.")));
        }
        inventory.setItem(31,QuestMenu.item(Material.ENDER_CHEST,"<aqua>Your private hoe locker",List.of(
                "<gray>Your hoe is stored when you leave.","<gray>Enter the fields to collect it.",
                "<yellow>Click to collect your hoe.")));
        inventory.setItem(40,QuestMenu.item(Material.BARRIER,"<red>Close",List.of()));
    }
    public void click(int slot,ClickType type){
        if(slot==40){player.closeInventory();return;}
        if(!plugin.farm().validUpgrader(player,station)){player.closeInventory();plugin.send(player,T.t("farm-menu.stand-next-to-the-fieldsmith", "<yellow>Stand next to the Fieldsmith Anvil to use it."));return;}
        if(slot==31){if(plugin.farm().inFarm(player))plugin.farm().equip(player);else plugin.send(player,T.t("farm-menu.step-into-the-fields-to", "<yellow>Step into the fields to collect your hoe."));return;}
        if(slot==34&&confirm!=null){
            int id=confirm;confirm=null;
            boolean bought=plugin.farm().purchase(player,id);fill();
            if(bought){
                // Repeated clicks on the old buy button cannot start buying another tier.
                choices.remove(34);
                inventory.setItem(34,QuestMenu.item(Material.LIME_STAINED_GLASS_PANE,"<green><bold>Ready for the fields",List.of(
                        "<gray>Your upgrade is unlocked.","<gray>Click the next hoe to review another upgrade.")));
            }
            return;
        }
        Integer id=choices.get(slot);if(id==null)return;
        var tier=plugin.farm().tier(id);if(tier==null){fill();return;}
        var data=plugin.questManager().data(player);
        boolean eligible=id==data.hoeTier()+1&&plugin.progression().level(data)>=tier.level();
        confirm=eligible?id:null;

        if(!eligible){
            String reason=id<=data.hoeTier()?"You already own this tier.":id!=data.hoeTier()+1?"Unlock the previous tier first.":"Reach Wayfarer level "+tier.level()+" first.";
            inventory.setItem(34,QuestMenu.item(Material.GRAY_CONCRETE,"<gray>Purchase unavailable",List.of("<yellow>"+reason)));
            return;
        }
        inventory.setItem(34,QuestMenu.item(Material.LIME_CONCRETE,"<green><bold>Buy for $"+Text.formatMoney(tier.cost()),List.of(
                "<white>"+Text.escape(tier.name()),
                "<gray>This replaces your current hoe tier.","<yellow>Click to buy.")));
    }
}
