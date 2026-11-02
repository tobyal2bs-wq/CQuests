package com.cquests.merchant;

import com.cquests.CQuestsPlugin;
import com.cquests.gui.*;
import com.cquests.util.Text;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.event.inventory.ClickType;
import org.bukkit.inventory.*;
import java.util.*;

public final class MerchantMenu implements LockedMenu {
    private final CQuestsPlugin plugin;private final Player player;private final String id;private final Inventory inventory;
    private final long revision;private Integer selected;
    private MerchantMenu(CQuestsPlugin plugin,Player player,String id){this.plugin=plugin;this.player=player;this.id=id;revision=plugin.merchants().get(id).revision();inventory=Bukkit.createInventory(this,45,Text.mm("<dark_gray>Travelling market"));fill();}
    public static void open(CQuestsPlugin plugin,Player player,String id){player.openInventory(new MerchantMenu(plugin,player,id).inventory);}
    public UUID viewer(){return player.getUniqueId();}public Inventory getInventory(){return inventory;}
    static String label(ItemStack item){return item==null?"None":item.getAmount()+" × "+Text.pretty(item.getType().name());}
    private void fill(){
        for(int i=0;i<45;i++)inventory.setItem(i,QuestMenu.item(Material.GRAY_STAINED_GLASS_PANE," ",List.of()));
        var d=plugin.merchants().get(id);inventory.setItem(4,QuestMenu.item(Material.EMERALD,"<gold><bold>"+d.name(),List.of("<gray>Choose an offer, then confirm.","<gray>Named/enchanting data must match the cost exactly.")));
        for(int i=0;i<7;i++){var offer=d.offers().get(i);if(offer!=null)inventory.setItem(10+i,QuestMenu.item(offer.reward().getType(),"<gold>Offer "+(i+1)+" <gray>• <white>"+label(offer.reward()),List.of("<gray>Give: <white>"+label(offer.first()),"<gray>Also: <white>"+label(offer.second()),"<gray>Money: <green>$"+Text.formatMoney(offer.money()),"<yellow>Click to review this trade.")));}
        inventory.setItem(40,QuestMenu.item(Material.BARRIER,"<red>Close",List.of()));
    }
    public void click(int slot,ClickType type){
        if(slot==40){player.closeInventory();return;}
        if(slot==31&&selected!=null){int offer=selected;selected=null;plugin.merchants().trade(player,id,offer,revision);player.closeInventory();return;}
        if(slot<10||slot>16)return;var d=plugin.merchants().get(id);
        if(d==null||d.revision()!=revision||!plugin.merchants().nearShop(player,id)){player.closeInventory();plugin.send(player,"<yellow>Shop changed. Speak to the merchant again.");return;}
        var offer=d.offers().get(slot-10);if(offer==null)return;selected=slot-10;
        inventory.setItem(22,offer.reward());
        inventory.setItem(31,QuestMenu.item(Material.LIME_CONCRETE,"<green><bold>Confirm one trade",List.of("<gray>Give: <white>"+label(offer.first()),"<gray>Also: <white>"+label(offer.second()),"<gray>Money: <green>$"+Text.formatMoney(offer.money()),"<gray>Receive: <white>"+label(offer.reward()),"<gray>No items move unless the whole trade fits.")));
    }
}
