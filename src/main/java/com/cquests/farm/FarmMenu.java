package com.cquests.farm;

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
    private final CQuestsPlugin plugin;private final Player player;private final Inventory inventory;
    private final Map<Integer,Integer> choices=new HashMap<>();private Integer confirm;
    private FarmMenu(CQuestsPlugin p,Player player){plugin=p;this.player=player;inventory=Bukkit.createInventory(this,45,Text.mm("<dark_gray>Aldmere Field Workshop"));}
    public static void open(CQuestsPlugin p,Player player){var m=new FarmMenu(p,player);m.fill();player.openInventory(m.inventory);}
    public UUID viewer(){return player.getUniqueId();}
    public Inventory getInventory(){return inventory;}
    private void fill(){
        choices.clear();confirm=null;
        for(int i=0;i<45;i++)inventory.setItem(i,QuestMenu.item(Material.GRAY_STAINED_GLASS_PANE," ",List.of()));
        var data=plugin.questManager().data(player);
        inventory.setItem(4,QuestMenu.item(Material.ANVIL,"<gold><bold>Your field workshop",List.of(
                "<white>Wayfarer level "+plugin.progression().level(data),"<gray>One wheat per hit. Personal tools only.")));
        int slot=10;
        for(var tier:plugin.farm().tiers()){
            if(slot>16)break;
            String status=tier.id()<=data.hoeTier()?"<green>Owned":tier.id()==data.hoeTier()+1?"<yellow>Available next":"<gray>Locked";
            inventory.setItem(slot,QuestMenu.item(tier.material(),"<gold><bold>"+Text.escape(tier.name()),List.of(
                    "<gray>Skill XP: <aqua>×"+tier.multiplier(),"<gray>Extra wheat: <yellow>"+Math.round(tier.chance()*100)+"%",
                    "<gray>Level required: <white>"+tier.level(),"<gray>Cost: <green>$"+Text.formatMoney(tier.cost()),status,
                    "<gray>Click to review. Nothing is charged yet.")));
            choices.put(slot++,tier.id());
        }
        inventory.setItem(31,QuestMenu.item(Material.ENDER_CHEST,"<aqua>Your private hoe locker",List.of(
                "<gray>Your current tier is stored automatically.","<gray>Enter the farm to equip it; leave to store it.",
                "<yellow>Click to equip or store your tool.")));
        inventory.setItem(40,QuestMenu.item(Material.BARRIER,"<red>Close",List.of()));
    }
    public void click(int slot,ClickType type){
        if(slot==40){player.closeInventory();return;}
        if(slot==31){if(plugin.farm().inFarm(player))plugin.farm().equip(player);else plugin.farm().strip(player);return;}
        if(slot==34&&confirm!=null){int id=confirm;confirm=null;plugin.farm().purchase(player,id);fill();return;}
        Integer id=choices.get(slot);if(id==null)return;
        var tier=plugin.farm().tier(id);if(tier==null){fill();return;}
        var data=plugin.questManager().data(player);
        boolean eligible=id==data.hoeTier()+1&&plugin.progression().level(data)>=tier.level();
        confirm=eligible?id:null;
        inventory.setItem(22,QuestMenu.item(tier.material(),"<gold>Review "+Text.escape(tier.name()),List.of(
                "<gray>Level "+tier.level()+" • <green>$"+Text.formatMoney(tier.cost()),"<aqua>XP ×"+tier.multiplier(),
                "<gray>Upgrades must follow the tier order.")));
        if(!eligible){
            String reason=id<=data.hoeTier()?"You already own this tier.":id!=data.hoeTier()+1?"Unlock the previous tier first.":"Reach Wayfarer level "+tier.level()+" first.";
            inventory.setItem(34,QuestMenu.item(Material.GRAY_CONCRETE,"<gray>Purchase unavailable",List.of("<yellow>"+reason)));
            return;
        }
        inventory.setItem(34,QuestMenu.item(Material.LIME_CONCRETE,"<green><bold>Confirm purchase",List.of(
                "<gray>Charges $"+Text.formatMoney(tier.cost())+" only if eligible.",
                "<gray>The tool stays bound to your personal locker.")));
    }
}
