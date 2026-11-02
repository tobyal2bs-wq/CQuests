package com.cquests.merchant;

import com.cquests.CQuestsPlugin;
import com.cquests.gui.*;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.event.inventory.ClickType;
import org.bukkit.inventory.*;
import java.util.*;

/** Ghost-slot editor: inventory items are copied, never taken or returned on close. */
public final class MerchantEditor implements LockedMenu {
    private final CQuestsPlugin plugin;private final Player player;private final String id;private final Inventory inventory;
    private long revision,money,sunflowers;private int selected,field=20;private ItemStack first,second,reward;
    private MerchantEditor(CQuestsPlugin plugin,Player player,String id){this.plugin=plugin;this.player=player;this.id=id;inventory=Bukkit.createInventory(this,54,"Merchant editor • OP only");load(0);}
    public static void open(CQuestsPlugin plugin,Player player,String id){if(!MerchantService.canEdit(player)||plugin.merchants().isDemo(id)||plugin.merchants().get(id)==null)return;player.openInventory(new MerchantEditor(plugin,player,id).inventory);}
    public UUID viewer(){return player.getUniqueId();}public Inventory getInventory(){return inventory;}
    private boolean allowed(){if(MerchantService.canEdit(player))return true;player.closeInventory();return false;}
    private void load(int slot){var d=plugin.merchants().get(id);if(d==null){player.closeInventory();return;}selected=slot;revision=d.revision();var offer=d.offers().get(slot);
        first=offer==null?null:offer.first();second=offer==null?null:offer.second();reward=offer==null?null:offer.reward();money=offer==null?0:offer.money();sunflowers=offer==null?0:offer.sunflowers();draw();}
    private void draw(){
        inventory.clear();for(int i=0;i<54;i++)inventory.setItem(i,QuestMenu.item(Material.GRAY_STAINED_GLASS_PANE," ",List.of()));
        for(int i=0;i<7;i++)inventory.setItem(i,QuestMenu.item(i==selected?Material.LIME_DYE:Material.PAPER,"<gold>Offer "+(i+1),List.of("<gray>Click to select. Save before switching.")));
        inventory.setItem(13,QuestMenu.item(Material.WRITABLE_BOOK,"<gold>"+id+" • offer "+(selected+1),List.of("<white>Select a field, then click an item in your inventory.","<gray>Copies its amount, name, lore and enchantments.","<gray>Right click an item field to clear it.","<yellow>Editing: "+(field==20?"First item cost":field==22?"Second item cost":field==24?"Reward":field==33?"Sunflower price":"Money price"))));
        preview(20,first,"First item cost");preview(22,second,"Second item cost (optional)");preview(24,reward,"Reward");
        inventory.setItem(31,QuestMenu.item(Material.GOLD_INGOT,"<gold>Money price: $"+money,List.of("<gray>Click to edit money with the buttons below.","<gray>Zero means no money charge. Items and money can combine.")));
        inventory.setItem(33,QuestMenu.item(Material.SUNFLOWER,"<gold>Sunflower Tokens: "+sunflowers,List.of("<gray>Click, then use the amount buttons.","<gray>Charges the saved discovery pouch; ordinary flowers do not count.")));
        int[] slots={36,37,38,39,40,41};long[] values={-1,1,-100,100,-1000,1000};
        for(int i=0;i<slots.length;i++)inventory.setItem(slots[i],QuestMenu.item(values[i]<0?Material.RED_DYE:Material.LIME_DYE,"<white>"+(values[i]>0?"+":"")+values[i],List.of("<gray>Adjust the selected item amount or money price.")));
        inventory.setItem(47,QuestMenu.item(Material.RED_CONCRETE,"<red>Delete selected offer",List.of("<gray>Removes this trade from the shop.")));
        inventory.setItem(49,QuestMenu.item(Material.EMERALD_BLOCK,"<green><bold>Save selected offer",List.of("<gray>Requires a reward and at least one item, money or token cost.")));
        inventory.setItem(51,QuestMenu.item(Material.BARRIER,"<red>Close",List.of("<gray>Unsaved changes are discarded.")));
    }
    private void preview(int slot,ItemStack item,String title){if(item==null){inventory.setItem(slot,QuestMenu.item(Material.LIGHT_GRAY_STAINED_GLASS_PANE,"<yellow>"+title,List.of("<gray>Click, then click a stack in your inventory.")));return;}
        ItemStack preview=item.clone();preview.editMeta(meta->{var lore=meta.lore()==null?new ArrayList<net.kyori.adventure.text.Component>():new ArrayList<>(meta.lore());lore.add(com.cquests.util.Text.mm("<yellow>Editor field: "+title));meta.lore(lore);});inventory.setItem(slot,preview);}
    public void capture(ItemStack item){
        if(!allowed())return;if(field==31||field==33){plugin.send(player,"<yellow>Use the amount buttons to set the selected price.");return;}
        if(item==null||item.getType().isAir()||!plugin.merchants().safeItem(item)){plugin.send(player,"<red>Use an ordinary item template. Bound tools, wands and container items cannot be traded.");return;}
        if(field==20)first=item.clone();else if(field==22)second=item.clone();else reward=item.clone();draw();
    }
    public void click(int slot,ClickType type){
        if(!allowed())return;if(slot==51){player.closeInventory();return;}
        if(slot>=0&&slot<7){load(slot);return;}
        if(slot==20||slot==22||slot==24||slot==31||slot==33){field=slot;if(type==ClickType.RIGHT&&slot!=31&&slot!=33){if(slot==20)first=null;else if(slot==22)second=null;else reward=null;}draw();return;}
        int delta=switch(slot){case 36->-1;case 37->1;case 38->-100;case 39->100;case 40->-1000;case 41->1000;default->0;};
        if(delta!=0){if(field==33)sunflowers=Math.max(0,Math.min(1_000_000_000L,sunflowers+delta));else if(field==31)money=Math.max(0,Math.min(1_000_000_000L,money+delta));else{ItemStack item=field==20?first:field==22?second:reward;if(item!=null)item.setAmount(Math.max(1,Math.min(item.getMaxStackSize(),item.getAmount()+delta)));}draw();return;}
        if(slot==47||slot==49){try{
            TradeOffer offer=slot==47?null:new TradeOffer(first,second,reward,money,sunflowers);
            if(!plugin.merchants().offer(player,id,selected,offer,revision)){plugin.send(player,"<yellow>Save rejected: merchant changed, permission changed or template is forbidden. Reopen the editor.");player.closeInventory();return;}
            plugin.send(player,"<green>Saved offer "+(selected+1)+" for "+id+".");load(selected);
        }catch(IllegalArgumentException e){plugin.send(player,"<red>"+e.getMessage());}}
    }
}
