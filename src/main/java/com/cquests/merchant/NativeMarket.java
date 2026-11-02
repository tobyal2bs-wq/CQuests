package com.cquests.merchant;

import com.cquests.CQuestsPlugin;
import com.cquests.util.Sched;
import com.cquests.util.Text;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.event.*;
import org.bukkit.event.inventory.*;
import org.bukkit.event.player.*;
import org.bukkit.inventory.*;
import org.bukkit.persistence.PersistentDataType;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/** Native trade presentation; all inputs/results are marked previews, never vanilla payments. */
public final class NativeMarket implements Listener {
    private final CQuestsPlugin plugin;private final NamespacedKey ghost;
    private final Map<UUID,Session> sessions=new ConcurrentHashMap<>();
    private static final class Session {
        final Player player;final Merchant merchant;final String id;final long revision;final List<Integer> slots;
        MerchantInventory inventory;int selected,generation;boolean queued;
        Session(Player p,Merchant m,MerchantDefinition d,List<Integer> slots){player=p;merchant=m;id=d.id();revision=d.revision();this.slots=List.copyOf(slots);}
    }
    public NativeMarket(CQuestsPlugin plugin){this.plugin=plugin;ghost=new NamespacedKey(plugin,"merchant_preview");}
    public boolean ghost(ItemStack item){return item!=null&&item.hasItemMeta()&&item.getItemMeta().getPersistentDataContainer().has(ghost,PersistentDataType.STRING);}
    private ItemStack preview(ItemStack template,String key,List<String> details){
        var item=template.clone();item.editMeta(m->{m.getPersistentDataContainer().set(ghost,PersistentDataType.STRING,key);var lore=new ArrayList<>(m.lore()==null?List.<net.kyori.adventure.text.Component>of():m.lore());details.forEach(s->lore.add(Text.mm(s)));lore.add(Text.mm("<dark_gray>Shop preview • payment comes from your inventory/pouch"));m.lore(lore);});return item;
    }
    public void open(Player player,String id){
        var d=plugin.merchants().get(id);if(d==null||!plugin.merchants().nearShop(player,id))return;
        player.closeInventory();purge(player);
        Merchant merchant=Bukkit.createMerchant(Text.mm(plugin.characters().label(id,d.name())));
        var slots=new ArrayList<Integer>();var recipes=new ArrayList<MerchantRecipe>();String nonce=UUID.randomUUID().toString();
        for(int i=0;i<d.offers().size();i++){
            var offer=d.offers().get(i);if(offer==null)continue;slots.add(i);
            var details=List.of("<gray>Items: <white>"+MerchantMenu.label(offer.first())+" + "+MerchantMenu.label(offer.second()),"<gray>Money: <green>$"+Text.formatMoney(offer.money()),"<gray>Sunflower Tokens: <yellow>"+offer.sunflowers());
            var ingredients=new ArrayList<ItemStack>();
            if(offer.first()!=null)ingredients.add(preview(offer.first(),nonce+":"+i+":a",details));
            if(offer.second()!=null)ingredients.add(preview(offer.second(),nonce+":"+i+":b",details));
            if(ingredients.size()<2&&offer.sunflowers()>0)ingredients.add(preview(new ItemStack(Material.SUNFLOWER,(int)Math.min(64,offer.sunflowers())),nonce+":"+i+":token",details));
            if(ingredients.size()<2&&offer.money()>0)ingredients.add(preview(new ItemStack(Material.GOLD_NUGGET),nonce+":"+i+":money",details));
            var recipe=new MerchantRecipe(preview(offer.reward(),nonce+":"+i+":result",details),0,Integer.MAX_VALUE,false,0,0);
            recipe.setIngredients(ingredients);recipes.add(recipe);
        }
        if(recipes.isEmpty()){plugin.send(player,"<gray>This merchant has no offers yet.");return;}
        merchant.setRecipes(recipes);var session=new Session(player,merchant,d,slots);sessions.put(player.getUniqueId(),session);
        try{var view=(InventoryView)player.getClass().getMethod("openMerchant",Merchant.class,boolean.class).invoke(player,merchant,true);if(view==null){sessions.remove(player.getUniqueId(),session);return;}session.inventory=(MerchantInventory)view.getTopInventory();paint(session);}
        catch(ReflectiveOperationException|RuntimeException e){sessions.remove(player.getUniqueId(),session);plugin.send(player,"<gray>The merchant window could not open. Please try again.");plugin.getLogger().warning("Merchant window could not open: "+e.getClass().getSimpleName());}
    }
    private Session session(org.bukkit.inventory.InventoryView view){
        var s=sessions.get(view.getPlayer().getUniqueId());return s!=null&&view.getTopInventory() instanceof MerchantInventory m&&m.getMerchant().equals(s.merchant)?s:null;
    }
    private void paint(Session s){
        if(session(s.player.getOpenInventory())!=s)return;
        var recipe=s.merchant.getRecipe(s.selected);var costs=recipe.getIngredients();
        s.inventory.setItem(0,costs.get(0));s.inventory.setItem(1,costs.size()>1?costs.get(1):null);
        s.inventory.setItem(2,recipe.getResult());
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void select(TradeSelectEvent event){var s=session(event.getView());if(s==null)return;event.setCancelled(true);if(event.getIndex()<0||event.getIndex()>=s.slots.size())return;s.selected=event.getIndex();s.generation++;Sched.entity(s.player,()->paint(s));}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void click(InventoryClickEvent event){
        var s=session(event.getView());if(s==null){
            if(ghost(event.getCurrentItem())||ghost(event.getCursor())||(event.getHotbarButton()>=0&&ghost(event.getWhoClicked().getInventory().getItem(event.getHotbarButton())))||(event.getClick()==ClickType.SWAP_OFFHAND&&ghost(event.getWhoClicked().getInventory().getItemInOffHand())))event.setCancelled(true);return;
        }
        event.setCancelled(true);
        if(event.getRawSlot()!=2||event.getClick()!=ClickType.LEFT||s.queued)return;
        int generation=s.generation,selection=s.selected;s.queued=true;
        var task=s.player.getScheduler().run(plugin,ignored->{try{
            if(session(s.player.getOpenInventory())!=s||s.generation!=generation)return;
            if(plugin.merchants().isDemo(s.id))plugin.send(s.player,"<aqua>Preview only. No items or payment moved.");
            else plugin.merchants().trade(s.player,s.id,s.slots.get(selection),s.revision);
            s.player.closeInventory();
        }finally{s.queued=false;}},()->s.queued=false);
        if(task==null)s.queued=false;
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void drag(InventoryDragEvent event){if(session(event.getView())!=null||ghost(event.getOldCursor()))event.setCancelled(true);}
    @EventHandler(priority=EventPriority.LOWEST)
    public void close(InventoryCloseEvent event){var s=session(event.getView());if(s==null)return;sessions.remove(s.player.getUniqueId(),s);event.getInventory().clear();purge(s.player);Sched.entityLater(s.player,1,()->purge(s.player));}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void move(InventoryMoveItemEvent event){if(ghost(event.getItem()))event.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void drop(PlayerDropItemEvent event){if(ghost(event.getItemDrop().getItemStack())){event.setCancelled(true);event.getItemDrop().remove();purge(event.getPlayer());}}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void use(PlayerInteractEvent event){if(ghost(event.getItem()))event.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false) public void spawn(org.bukkit.event.entity.ItemSpawnEvent event){if(ghost(event.getEntity().getItemStack()))event.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false) public void swap(PlayerSwapHandItemsEvent event){if(ghost(event.getMainHandItem())||ghost(event.getOffHandItem()))event.setCancelled(true);}
    @EventHandler public void join(PlayerJoinEvent event){purge(event.getPlayer());Sched.entityLater(event.getPlayer(),1,()->purge(event.getPlayer()));}
    @EventHandler(priority=EventPriority.LOWEST) public void quit(PlayerQuitEvent event){var s=sessions.remove(event.getPlayer().getUniqueId());if(s!=null&&s.inventory!=null)s.inventory.clear();purge(event.getPlayer());}
    @EventHandler(priority=EventPriority.HIGHEST) public void death(org.bukkit.event.entity.PlayerDeathEvent event){event.getDrops().removeIf(this::ghost);purge(event.getEntity());}
    public void purge(Player player){for(int i=0;i<player.getInventory().getSize();i++)if(ghost(player.getInventory().getItem(i)))player.getInventory().setItem(i,null);if(ghost(player.getItemOnCursor()))player.setItemOnCursor(null);}
    public void clear(){for(var s:List.copyOf(sessions.values()))Sched.entity(s.player,()->{if(session(s.player.getOpenInventory())==s)s.player.closeInventory();purge(s.player);});}
}
