package com.cquests.merchant;

import com.cquests.CQuestsPlugin;
import com.cquests.farm.EconomyBridge;
import com.cquests.npc.SafePlacement;
import com.cquests.util.*;
import org.bukkit.*;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.*;
import org.bukkit.inventory.*;
import org.bukkit.inventory.meta.*;
import org.bukkit.persistence.PersistentDataType;
import java.io.File;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** Five bounded native pathfinders. Entity state stays on entity schedulers; trading stays on the player. */
public final class MerchantService {
    private final CQuestsPlugin plugin;
    private final File file;
    private final NamespacedKey tag,wand;
    private final EconomyBridge economy=new EconomyBridge();
    private final TrailPreview preview=new TrailPreview();
    private volatile Map<String,MerchantDefinition> definitions=Map.of();
    private final Map<String,Walk> live=new ConcurrentHashMap<>();
    private record Ticket(World world,int x,int z) {Location location(){return new Location(world,x*16,world.getMinHeight(),z*16);}}
    private final Map<Ticket,Integer> tickets=new HashMap<>();
    private final Map<UUID,Long> tradeCooldown=new ConcurrentHashMap<>();
    private final Set<UUID> editing=ConcurrentHashMap.newKeySet();
    private final AtomicLong revisions=new AtomicLong(System.currentTimeMillis());
    private final AtomicInteger writes=new AtomicInteger();
    private final ExecutorService writer=Executors.newSingleThreadExecutor(r->{var t=new Thread(r,"CQuests-merchant-writer");t.setDaemon(true);return t;});
    private YamlConfiguration yaml;
    private volatile boolean running=true;
    private io.papermc.paper.threadedregions.scheduler.ScheduledTask startup;
    private static final class Walk {
        volatile Villager entity;volatile MerchantPoint position;volatile boolean shop,blocked;
        int next,ticks;final List<MerchantPoint> route;final Set<Ticket> held=new HashSet<>();
        Walk(List<MerchantPoint> route){this.route=route;}
    }
    public MerchantService(CQuestsPlugin plugin){
        this.plugin=plugin;file=new File(plugin.getDataFolder(),"merchants.yml");tag=new NamespacedKey(plugin,"travelling_merchant");wand=new NamespacedKey(plugin,"merchant_wand");load();
    }
    public Collection<MerchantDefinition> all(){return definitions.values().stream().sorted(Comparator.comparing(MerchantDefinition::id)).toList();}
    public MerchantDefinition get(String id){return definitions.get(id);}
    public String id(Entity entity){return entity.getPersistentDataContainer().get(tag,PersistentDataType.STRING);}
    public boolean current(Entity entity){String id=id(entity);Walk w=id==null?null:live.get(id);return w!=null&&w.entity==entity;}
    public boolean safeItem(ItemStack item){
        if(item==null||item.getType().isAir())return true;
        if(plugin.farm().marked(item)||plugin.farmCommand().wand(item)||item.getItemMeta().getPersistentDataContainer().has(wand,PersistentDataType.STRING))return false;
        var meta=item.getItemMeta();
        return !(meta instanceof BundleMeta)&&!(meta instanceof BlockStateMeta state&&state.getBlockState() instanceof InventoryHolder);
    }
    public static boolean canEdit(Player player){return player.isOp();}
    public static boolean editGesture(Player player){return player.isSneaking()||(player.getCurrentInput()!=null&&player.getCurrentInput().isSneak());}
    private ItemStack item(String path){
        Object raw=yaml.get(path);if(raw instanceof ItemStack stack)return stack.clone();
        if(raw instanceof String text){String[] parts=text.split(" ");return new ItemStack(Material.valueOf(parts[0]),parts.length>1?Integer.parseInt(parts[1]):1);}return null;
    }
    private synchronized void load(){
        yaml=YamlConfiguration.loadConfiguration(file);Map<String,MerchantDefinition> found=new LinkedHashMap<>();
        var root=yaml.getConfigurationSection("merchants");
        if(root!=null)for(String id:root.getKeys(false))try{
            if(!id.matches("[a-z0-9_-]{1,40}"))continue;String p="merchants."+id+".";
            List<TradeOffer> offers=new ArrayList<>(Collections.nCopies(7,null));
            for(int i=0;i<7;i++)try{String t=p+"offers."+(i+1)+".";ItemStack reward=item(t+"reward");if(reward==null)continue;
                TradeOffer offer=new TradeOffer(item(t+"cost-a"),item(t+"cost-b"),reward,yaml.getLong(t+"money",0));
                if(!safeItem(offer.first())||!safeItem(offer.second())||!safeItem(offer.reward()))throw new IllegalArgumentException("Bound tools and filled-container templates are not tradeable");offers.set(i,offer);
            }catch(RuntimeException e){plugin.getLogger().warning("Merchant "+id+" offer "+(i+1)+" disabled: "+e.getMessage());}
            List<MerchantPoint> route=new ArrayList<>();for(String value:yaml.getStringList(p+"route")){MerchantPoint point=MerchantPoint.decode(value);if(point==null)throw new IllegalArgumentException("Invalid route point");route.add(point);}
            if(route.size()>64)throw new IllegalArgumentException("Maximum 64 route points");
            found.put(id,new MerchantDefinition(id,yaml.getString(p+"name",id),yaml.getString(p+"profession","NONE"),
                    MerchantPoint.decode(yaml.getString(p+"spawn")),route,MerchantPoint.decode(yaml.getString(p+"shop")),offers,yaml.getBoolean(p+"enabled",false),revisions.incrementAndGet()));
        }catch(RuntimeException e){plugin.getLogger().warning("Merchant "+id+" disabled: "+e.getMessage());}
        definitions=Map.copyOf(found);
    }
    public synchronized void start(){
        if(startup!=null)startup.cancel();
        // Chunk snapshot requests must start after world bootstrap, not inside plugin enable.
        startup=Sched.globalTimer(task->{task.cancel();if(running)for(var d:all())if(d.enabled())walk(d.id(),null);},20,20);
    }
    public String status(String id){Walk walk=live.get(id);return walk==null?"Not spawned":walk.entity==null?"Validating route":walk.blocked?"Route blocked":walk.shop?"Open":"Travelling";}
    public synchronized void reload(){preview.clearAll();stopAll();if(writes.get()==0)load();else plugin.getLogger().info("Merchant saves are pending; retaining the latest in-memory configuration.");start();}
    private synchronized void save(MerchantDefinition d){
        Map<String,MerchantDefinition> copy=new LinkedHashMap<>(definitions);copy.put(d.id(),d);definitions=Map.copyOf(copy);
        String p="merchants."+d.id()+".";yaml.set(p+"name",d.name());yaml.set(p+"profession",d.profession());yaml.set(p+"enabled",d.enabled());
        yaml.set(p+"spawn",d.spawn()==null?null:d.spawn().encode());yaml.set(p+"shop",d.shop()==null?null:d.shop().encode());yaml.set(p+"route",d.route().stream().map(MerchantPoint::encode).toList());
        for(int i=0;i<7;i++){String t=p+"offers."+(i+1);TradeOffer offer=d.offers().get(i);yaml.set(t,null);if(offer!=null){yaml.set(t+".cost-a",offer.first());yaml.set(t+".cost-b",offer.second());yaml.set(t+".reward",offer.reward());yaml.set(t+".money",offer.money());}}
        String snapshot=yaml.saveToString();writes.incrementAndGet();writer.execute(()->{
            try{Path temp=file.toPath().resolveSibling("merchants.yml.tmp");Files.writeString(temp,snapshot);
                try{Files.move(temp,file.toPath(),StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);}catch(AtomicMoveNotSupportedException e){Files.move(temp,file.toPath(),StandardCopyOption.REPLACE_EXISTING);}
            }catch(Exception e){plugin.getLogger().severe("Merchant save failed: "+e.getMessage());}finally{writes.decrementAndGet();}
        });
    }
    private MerchantDefinition changed(MerchantDefinition d,MerchantPoint spawn,List<MerchantPoint> route,MerchantPoint shop,List<TradeOffer> offers,boolean enabled){
        return new MerchantDefinition(d.id(),d.name(),d.profession(),spawn,route,shop,offers,enabled,revisions.incrementAndGet());
    }
    public synchronized boolean offer(Player player,String id,int slot,TradeOffer offer,long expected){
        MerchantDefinition d=get(id);if(!canEdit(player)||!running||d==null||d.revision()!=expected||slot<0||slot>=7)return false;
        if(offer!=null&&(!safeItem(offer.first())||!safeItem(offer.second())||!safeItem(offer.reward())))return false;
        List<TradeOffer> offers=new ArrayList<>(d.offers());offers.set(slot,offer);save(changed(d,d.spawn(),d.route(),d.shop(),offers,d.enabled()));return true;
    }
    public void setPoint(Player player,String id,String kind,Location loc){
        MerchantDefinition before=get(id);if(!canEdit(player)||before==null||!running||!Set.of("spawn","point","shop","end").contains(kind))return;
        if(!editing.add(player.getUniqueId())){plugin.send(player,"<yellow>Wait for the previous point to finish validating.");return;}
        var future=kind.equals("spawn")?SafePlacement.validate(loc):SafePlacement.validateWalkStop(loc);
        future.whenComplete((valid,error)->Sched.entity(player,()->{try{
            synchronized(this){
                MerchantDefinition d=get(id);if(!canEdit(player)||!running||d==null||d.revision()!=before.revision()){plugin.send(player,"<yellow>Merchant changed; select the point again.");return;}
                if(error!=null||!Boolean.TRUE.equals(valid)){plugin.send(player,"<red>Use solid safe ground with headroom. Spawn points must be outdoors.");return;}
                MerchantPoint point=MerchantPoint.at(loc);MerchantPoint spawn=kind.equals("spawn")?point:d.spawn(),shop=(kind.equals("shop")||kind.equals("end"))?point:d.shop();List<MerchantPoint> route=new ArrayList<>(d.route());
                if(kind.equals("point")){if(route.size()>=64){plugin.send(player,"<red>Maximum 64 route points.");return;}route.add(point);}
                List<MerchantPoint> points=new ArrayList<>();if(spawn!=null)points.add(spawn);points.addAll(route);if(shop!=null)points.add(shop);
                if(points.stream().anyMatch(v->!v.world().equals(point.world()))){plugin.send(player,"<red>Keep one merchant's entire route in one world.");return;}
                stop(id);save(changed(d,spawn,route,shop,d.offers(),false));if(kind.equals("point"))preview.show(player,loc);if(kind.equals("end")){preview.clear(player);walk(id,player);}plugin.send(player,"<green>Saved "+kind+" for "+id+" <gray>• "+route.size()+" trail points."+(kind.equals("end")?"":" Finish with /cq merchant end "+id+" while facing the store direction."));
            }
        }finally{editing.remove(player.getUniqueId());}}));
    }
    public synchronized void undo(Player player,String id,boolean clear){
        MerchantDefinition d=get(id);if(!canEdit(player)||d==null||!running)return;var route=new ArrayList<>(d.route());if(clear)route.clear();else if(!route.isEmpty())route.removeLast();
        preview.clear(player);stop(id);save(changed(d,d.spawn(),route,d.shop(),d.offers(),false));plugin.send(player,"<green>Route now has "+route.size()+" points.");
    }
    public ItemStack wand(String id){var item=new ItemStack(Material.STICK);item.editMeta(m->{m.displayName(Text.mm("<gold>Merchant route: "+Text.escape(id)));m.lore(List.of(Text.mm("<gray>Right click ground: mark trail. Left click: undo.")));m.getPersistentDataContainer().set(wand,PersistentDataType.STRING,id);});return item;}
    public void showTrail(Player player,String id){preview.clear(player);var d=get(id);if(canEdit(player)&&d!=null)for(var point:d.route()){var loc=point.location();if(loc!=null)preview.show(player,loc);}}
    public String wandId(ItemStack item){return item==null||!item.hasItemMeta()?null:item.getItemMeta().getPersistentDataContainer().get(wand,PersistentDataType.STRING);}
    public synchronized void walk(String id,Player feedback){
        MerchantDefinition d=get(id);if(d==null||!running)return;
        if(d.spawn()==null||d.shop()==null){tell(feedback,"<yellow>Set both /cq merchant spawn "+id+" and /cq merchant shop "+id+" first.");return;}
        List<MerchantPoint> route=new ArrayList<>();route.add(d.spawn());route.addAll(d.route());route.add(d.shop());
        for(int i=0;i<route.size();i++){
            Location loc=route.get(i).location();if(loc==null){tell(feedback,"<red>Merchant world is not loaded.");return;}
            if(!loc.getWorld().equals(d.spawn().location().getWorld())||(i>0&&loc.distanceSquared(route.get(i-1).location())>32*32)){tell(feedback,"<red>Keep successive route points within 32 blocks in one world.");return;}
        }
        Set<Ticket> required=new LinkedHashSet<>();
        for(int i=1;i<route.size();i++){Location a=route.get(i-1).location(),b=route.get(i).location();
            for(int x=Math.min(a.getBlockX()>>4,b.getBlockX()>>4);x<=Math.max(a.getBlockX()>>4,b.getBlockX()>>4);x++)
                for(int z=Math.min(a.getBlockZ()>>4,b.getBlockZ()>>4);z<=Math.max(a.getBlockZ()>>4,b.getBlockZ()>>4);z++)required.add(new Ticket(a.getWorld(),x,z));}
        if(required.size()>128){tell(feedback,"<red>Route is too large: use at most 128 distinct chunks.");return;}
        stop(id);Walk walk=new Walk(List.copyOf(route.subList(1,route.size())));live.put(id,walk);
        CompletableFuture<Boolean> valid=hold(id,walk,required).thenCompose(ok->ok?SafePlacement.validate(d.spawn().location()):CompletableFuture.completedFuture(false));
        for(MerchantPoint point:walk.route)valid=valid.thenCompose(ok->ok?SafePlacement.validateWalkStop(point.location()):CompletableFuture.completedFuture(false));
        valid.whenComplete((ok,error)->{
            if(!running||live.get(id)!=walk)return;
            if(error!=null||!Boolean.TRUE.equals(ok)){synchronized(this){if(live.get(id)==walk)stop(id);}tell(feedback,"<red>The route has an unsafe stop. Re-select it on solid ground.");return;}
            Location at=d.spawn().location();Sched.at(at,()->{
                if(!running||live.get(id)!=walk)return;
                Villager entity=at.getWorld().spawn(at,Villager.class,v->{v.getPersistentDataContainer().set(tag,PersistentDataType.STRING,id);v.setPersistent(false);v.setInvulnerable(true);v.setSilent(true);v.setCollidable(false);v.setCanPickupItems(false);v.setAdult();v.setAgeLock(true);var profession=Registry.VILLAGER_PROFESSION.get(NamespacedKey.minecraft(d.profession().toLowerCase(Locale.ROOT)));if(profession!=null)v.setProfession(profession);v.setRemoveWhenFarAway(false);v.customName(Text.mm("<bold>"+d.name()+"</bold> <gray>• Travelling"));v.setCustomNameVisible(true);});
                walk.entity=entity;walk.position=MerchantPoint.at(at);
                entity.getScheduler().runAtFixedRate(plugin,t->{if(!running||live.get(id)!=walk){t.cancel();entity.remove();return;}tick(id,walk);},()->{synchronized(this){if(live.get(id)==walk)stop(id);}},10,10);
                synchronized(this){MerchantDefinition current=get(id);if(current!=null&&live.get(id)==walk)save(changed(current,current.spawn(),current.route(),current.shop(),current.offers(),true));}
                tell(feedback,"<green>"+id+" is walking to the store. Trading opens on arrival.");
            });
        });
    }
    private CompletableFuture<Boolean> hold(String id,Walk walk,Set<Ticket> required){
        List<CompletableFuture<Void>> tasks=new ArrayList<>();
        for(Ticket ticket:required){CompletableFuture<Void> task=new CompletableFuture<>();tasks.add(task);
            ticket.world().getChunkAtAsync(ticket.x(),ticket.z(),true).whenComplete((chunk,error)->{
                if(error!=null){task.completeExceptionally(error);return;}
                try{Sched.at(ticket.location(),()->{try{synchronized(this){if(running&&live.get(id)==walk){
                    int count=tickets.getOrDefault(ticket,0);if(count==0)chunk.addPluginChunkTicket(plugin);
                    tickets.put(ticket,count+1);walk.held.add(ticket);
                }}task.complete(null);}catch(Throwable e){task.completeExceptionally(e);}});}catch(Throwable e){task.completeExceptionally(e);}
            });
        }
        return CompletableFuture.allOf(tasks.toArray(CompletableFuture[]::new)).thenApply(ignored->running&&live.get(id)==walk);
    }
    private void release(Walk walk){
        for(Ticket ticket:walk.held){if(!plugin.isEnabled())continue;
            Sched.at(ticket.location(),()->{synchronized(this){Integer count=tickets.get(ticket);if(count==null)return;
                if(count==1){tickets.remove(ticket);ticket.world().removePluginChunkTicket(ticket.x(),ticket.z(),plugin);}else tickets.put(ticket,count-1);
            }});
        }
        walk.held.clear();
    }
    private void tick(String id,Walk walk){
        Villager entity=walk.entity;Location current=entity.getLocation();walk.position=MerchantPoint.at(current);
        if(walk.shop||walk.blocked)return;
        Location target=walk.route.get(walk.next).location();
        if(target==null||!current.getWorld().equals(target.getWorld())){blocked(id,walk);return;}
        if(current.distanceSquared(target)<=1.0){
            if(++walk.next>=walk.route.size()){walk.shop=true;entity.getPathfinder().stopPathfinding();entity.setAI(false);entity.setRotation(walk.route.getLast().yaw(),0);var d=get(id);entity.customName(Text.mm("<bold>"+(d==null?id:d.name())+"</bold> <green>• Open"));return;}
            walk.ticks=0;target=walk.route.get(walk.next).location();
        }
        walk.ticks+=10;if(walk.ticks>1200){blocked(id,walk);return;}
        if(walk.ticks%20==10)entity.getPathfinder().moveTo(target,.8);
    }
    private void blocked(String id,Walk walk){walk.blocked=true;walk.entity.getPathfinder().stopPathfinding();walk.entity.setAI(false);var d=get(id);walk.entity.customName(Text.mm("<bold>"+(d==null?id:d.name())+"</bold> <red>• Route blocked"));plugin.getLogger().warning("Merchant "+id+" route blocked. Repair the path and use /cq merchant walk "+id+".");}
    public boolean nearShop(Player player,String id){
        Walk walk=live.get(id);MerchantDefinition d=get(id);if(!running||!player.isOnline()||d==null||d.shop()==null||walk==null||!walk.shop||walk.position==null)return false;
        Location loc=walk.position.location(),shop=d.shop().location();return loc!=null&&shop!=null&&loc.getWorld().equals(shop.getWorld())&&loc.distanceSquared(shop)<=4&&loc.getWorld().equals(player.getWorld())&&loc.distanceSquared(player.getLocation())<=64;
    }
    public synchronized boolean trade(Player player,String id,int slot,long revision){
        MerchantDefinition d=get(id);if(d==null||d.revision()!=revision||!nearShop(player,id)||slot<0||slot>=7){plugin.send(player,"<yellow>This offer changed or the merchant is out of reach. Open the shop again.");return false;}
        TradeOffer offer=d.offers().get(slot);if(offer==null)return false;long now=System.nanoTime();Long due=tradeCooldown.get(player.getUniqueId());if(due!=null&&now<due)return false;
        tradeCooldown.put(player.getUniqueId(),now+200_000_000L);
        ItemStack[] before=player.getInventory().getStorageContents(),after=BarterInventory.exchange(before,offer);
        if(after==null){plugin.send(player,"<yellow>You need the exact requested items and room for the reward. Nothing was taken.");return false;}
        var payment=economy.charge(player,offer.money());if(payment==null){plugin.send(player,"<red>The money payment was declined or Vault is unavailable. Your items were kept.");return false;}
        try{player.getInventory().setStorageContents(after);}catch(RuntimeException e){
            try{player.getInventory().setStorageContents(before);}catch(RuntimeException rollback){plugin.getLogger().severe("Merchant inventory rollback failed for "+player.getUniqueId()+": "+rollback);}
            finally{if(!payment.refund())plugin.getLogger().severe("Merchant refund failed for "+player.getUniqueId()+" amount "+offer.money());}
            plugin.getLogger().severe("Merchant trade commit failed for "+player.getUniqueId()+": "+e);plugin.send(player,"<red>Trade failed. Payment rollback was attempted; contact an operator if your balance is incorrect.");return false;
        }
        player.playSound(player.getLocation(),Sound.ENTITY_VILLAGER_YES,.7f,1.1f);plugin.send(player,"<green>Trade complete.");return true;
    }
    public void interact(Player player,String id,boolean editingGesture){
        if(get(id)==null)return;
        if(editingGesture&&canEdit(player)){MerchantEditor.open(plugin,player,id);return;}
        if(!nearShop(player,id)){plugin.send(player,"<yellow>Meet this merchant at the store after they finish walking.");return;}
        MerchantMenu.open(plugin,player,id);
    }
    public synchronized void disable(Player player,String id){MerchantDefinition d=get(id);if(!canEdit(player)||d==null||!running)return;stop(id);save(changed(d,d.spawn(),d.route(),d.shop(),d.offers(),false));plugin.send(player,"<gray>Merchant disabled; route and trades retained.");}
    private void stop(String id){Walk walk=live.remove(id);if(walk!=null){release(walk);if(walk.entity!=null&&plugin.isEnabled())Sched.entity(walk.entity,walk.entity::remove);}}
    private void stopAll(){for(String id:List.copyOf(live.keySet()))stop(id);}
    private void tell(Player player,String message){if(player!=null)Sched.entity(player,()->plugin.send(player,message));else plugin.getLogger().info(Text.plain(Text.mm(message)));}
    public void forget(Player player){preview.clear(player);tradeCooldown.remove(player.getUniqueId());editing.remove(player.getUniqueId());}
    public synchronized void shutdown(){running=false;preview.discard();if(startup!=null)startup.cancel();stopAll();writer.shutdown();try{if(!writer.awaitTermination(10,TimeUnit.SECONDS))plugin.getLogger().warning("Merchant saves did not drain within 10 seconds");}catch(InterruptedException e){Thread.currentThread().interrupt();}}
}
