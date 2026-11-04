package com.cquests.farm;

import com.cquests.T;

import com.cquests.CQuestsPlugin;
import com.cquests.model.ObjectiveType;
import com.cquests.util.Sched;
import com.cquests.util.Text;
import com.cquests.npc.WorldGuardHook;
import org.bukkit.*;
import org.bukkit.block.Block;
import org.bukkit.block.data.Ageable;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.persistence.PersistentDataType;
import java.io.File;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;

/** Wheat state belongs to block regions; rewards and inventories belong to each player's scheduler. */
public final class FarmService {
    public record Tier(int id,String name,Material material,long cost,int level,double multiplier,double chance,int cooldown) {}
    public record Spot(String world,int x,int y,int z) {
        public Location location(){World w=Bukkit.getWorld(world);return w==null?null:new Location(w,x,y,z);}
        public String encode(){return world+";"+x+";"+y+";"+z;}
        public static Spot decode(String s){String[] p=s.split(";");if(p.length!=4)return null;try{return new Spot(p[0],Integer.parseInt(p[1]),Integer.parseInt(p[2]),Integer.parseInt(p[3]));}catch(NumberFormatException e){return null;}}
    }
    private final CQuestsPlugin plugin;
    private final File file,pendingFile;
    private final NamespacedKey hoeKey,ownerKey,tierKey,anvilKey;
    private volatile Set<Spot> upgraders=Set.of();
    private final Map<UUID,Long> cooldowns=new ConcurrentHashMap<>();
    private final Set<UUID> inside=ConcurrentHashMap.newKeySet();
    private final Set<Spot> pending=ConcurrentHashMap.newKeySet();
    // Accessed only by the single writer after a successful atomic replacement.
    private Set<Spot> savedPending;
    private volatile List<FarmArea> areas=List.of();
    private volatile Map<Integer,Tier> tiers=Map.of();
    private final EconomyBridge economy=new EconomyBridge();
    private final ExecutorService writer=Executors.newSingleThreadExecutor(r->{Thread t=new Thread(r,"CQuests-farm-writer");t.setDaemon(true);return t;});
    private volatile boolean running=true;
    private boolean enabled,blockCommands,particles;
    private long xp; private int regrow;
    private volatile YamlConfiguration config;
    public FarmService(CQuestsPlugin plugin){
        this.plugin=plugin;file=new File(plugin.getDataFolder(),"farming.yml");pendingFile=new File(plugin.getDataFolder(),"farm-regrowth.yml");
        hoeKey=new NamespacedKey(plugin,"farm_hoe");ownerKey=new NamespacedKey(plugin,"farm_owner");tierKey=new NamespacedKey(plugin,"farm_tier");
        anvilKey=new NamespacedKey(plugin,"farm_upgrader");
        reload();
        for(String s:YamlConfiguration.loadConfiguration(pendingFile).getStringList("pending")){
            Spot spot=Spot.decode(s);if(spot!=null)pending.add(spot);
        }
        restoreLoaded();
    }
    public synchronized void reload(){
        config=YamlConfiguration.loadConfiguration(file);
        enabled=config.getBoolean("enabled",true);blockCommands=config.getBoolean("harvest.commands-blocked",true);
        particles=config.getBoolean("harvest.particles",true);xp=Math.max(1,config.getLong("harvest.xp-per-wheat",10));
        regrow=Math.max(1,config.getInt("harvest.regrow-ticks",20));
        Map<Integer,Tier> loaded=new TreeMap<>();
        var root=config.getConfigurationSection("tiers");
        if(root!=null)for(String key:root.getKeys(false))try{
            int n=Integer.parseInt(key);String p="tiers."+key+".";
            Material material=Material.matchMaterial(config.getString(p+"material","WOODEN_HOE"));
            if(n<1||material==null||!material.name().endsWith("_HOE"))continue;
            loaded.put(n,new Tier(n,config.getString(p+"name","Field Tool "+n),material,Math.max(0,config.getLong(p+"cost")),
                    Math.max(1,config.getInt(p+"level",1)),Math.max(1,Math.min(10,config.getDouble(p+"multiplier",1))),
                    Math.max(0,Math.min(1,config.getDouble(p+"double-chance",0))),Math.max(1,config.getInt(p+"cooldown-ticks",5))));
        }catch(NumberFormatException ignored){}
        tiers=Map.copyOf(loaded);
        List<FarmArea> list=new ArrayList<>();var ar=config.getConfigurationSection("areas");
        if(ar!=null)for(String id:ar.getKeys(false))try{
            String p="areas."+id+".";
            List<Polygon.Vertex> vertices=new ArrayList<>();
            for(String s:config.getStringList(p+"vertices")){String[] v=s.split(",");vertices.add(new Polygon.Vertex(Integer.parseInt(v[0]),Integer.parseInt(v[1])));}
            List<Integer> bounds=config.getIntegerList(p+"bounds");
            if(bounds.size()!=6)continue;
            list.add(new FarmArea(id,config.getString(p+"world","world"),config.getString(p+"region",""),
                    bounds.get(1),bounds.get(4),new Polygon(vertices),config.getBoolean(p+"outside"),bounds.stream().mapToInt(Integer::intValue).toArray()));
        }catch(RuntimeException e){plugin.getLogger().warning("Farm area "+id+" is invalid and remains disabled: "+e.getMessage());}
        areas=List.copyOf(list);upgraders=readUpgraders();economy.refresh();
    }
    public Collection<Tier> tiers(){return tiers.values().stream().sorted(Comparator.comparingInt(Tier::id)).toList();}
    public Tier tier(int id){return tiers.get(id);}
    public boolean blockCommands(){return blockCommands;}
    public boolean marked(ItemStack item){return item!=null&&item.hasItemMeta()&&item.getItemMeta().getPersistentDataContainer().has(hoeKey,PersistentDataType.BYTE);}
    public boolean owned(Player player,ItemStack item){
        if(!marked(item))return false;
        var data=item.getItemMeta().getPersistentDataContainer();
        return player.getUniqueId().toString().equals(data.get(ownerKey,PersistentDataType.STRING))
                &&plugin.questManager().data(player).hoeTier()==data.getOrDefault(tierKey,PersistentDataType.INTEGER,-1);
    }
    public ItemStack tool(Player player,Tier tier){
        ItemStack item=new ItemStack(tier.material());
        item.editMeta(meta->{
            meta.displayName(Text.mm("<!italic><gold><bold>"+Text.escape(tier.name())));
            meta.lore(List.of(Text.mm(T.t("farm-service.personal-farm-tool-wheat-only", "<!italic><gray>Personal farm tool • wheat only")),
                    Text.mm(T.t("farm-service.skill-xp-extra-wheat", "<!italic><aqua>Skill XP ×<multiplier> <gray>• extra wheat <chance>%", "multiplier", tier.multiplier(), "chance", Math.round(tier.chance()*100))),
                    Text.mm(T.t("farm-service.returns-to-your-private-locker", "<!italic><gray>Returns to your private locker when you leave."))));
            meta.setUnbreakable(true);
            var p=meta.getPersistentDataContainer();p.set(hoeKey,PersistentDataType.BYTE,(byte)1);
            p.set(ownerKey,PersistentDataType.STRING,player.getUniqueId().toString());p.set(tierKey,PersistentDataType.INTEGER,tier.id());
        });return item;
    }
    public FarmArea area(Location loc){
        if(!enabled||areas.isEmpty())return null;
        for(FarmArea area:areas)if(area.candidate(loc.getWorld().getName(),loc.getBlockX(),loc.getBlockY(),loc.getBlockZ())
                &&WorldGuardHook.contains(loc,area.region()))return area;
        return null;
    }
    public boolean inFarm(Player player){
        Location loc=player.getLocation();
        // A player's feet can be one block above the clicked crop. Region Y bounds remain strict for harvesting.
        return area(loc)!=null||area(loc.clone().subtract(0,1,0))!=null;
    }
    public void update(Player player){
        update(player,true);
    }
    public void update(Player player,boolean auditInventory){
        applyUpdate(player,auditInventory,inFarm(player));
    }
    /** The display loop reuses this exact check instead of querying WorldGuard a second time. */
    /** {@code audit} scans the inventory for stray farm tools; the display timer asks for it every 2 seconds, not every refresh. */
    public boolean updateAndCheck(Player player,boolean audit){
        boolean isInside=inFarm(player);applyUpdate(player,audit,isInside);return isInside;
    }
    private void applyUpdate(Player player,boolean auditInventory,boolean isInside){
        if(isInside){
            boolean entered=inside.add(player.getUniqueId());
            if(entered){plugin.send(player,T.t("farm-service.harvest-grounds-commands-are-paused", "<gold>Harvest grounds <gray>• commands are paused; your tool is bound to this area."));equip(player);}
            if(!entered&&!auditInventory)return;
            int count=0;boolean invalid=marked(player.getItemOnCursor());
            for(ItemStack item:player.getInventory().getContents())if(marked(item)){count+=item.getAmount();invalid|=!owned(player,item);}
            if(invalid||count>1){strip(player);equip(player);}
        }else if(inside.remove(player.getUniqueId())||(auditInventory&&hasTool(player))){
            strip(player);cooldowns.remove(player.getUniqueId());
            player.sendActionBar(Text.mm(T.t("farm-service.your-hoe-is-safe-in", "<gray>Your hoe is safe in your private field locker.")));
        }
    }
    private boolean hasTool(Player player){for(ItemStack item:player.getInventory().getContents())if(marked(item))return true;return marked(player.getItemOnCursor());}
    public void strip(Player player){
        for(int i=0;i<player.getInventory().getSize();i++)if(marked(player.getInventory().getItem(i)))player.getInventory().setItem(i,null);
        if(marked(player.getItemOnCursor()))player.setItemOnCursor(null);
    }
    /** Wheat and its farmland inside a saved farm: only the farm hoe may take them. */
    public boolean protectedCrop(Block block){
        Material type=block.getType();
        if(type!=Material.WHEAT&&type!=Material.FARMLAND&&!(type==Material.AIR&&block.getRelative(0,-1,0).getType()==Material.FARMLAND))return false;
        return area(block.getLocation())!=null;
    }
    /** Explains why a crop did not break, at most once every 3 seconds. */
    public void hint(Player player){
        long now=System.currentTimeMillis();Long last=hints.get(player.getUniqueId());
        if(last!=null&&now-last<3000)return;hints.put(player.getUniqueId(),now);
        if(player.getGameMode()==GameMode.CREATIVE){player.sendActionBar(Text.mm(T.t("farm-service.switch-to-survival-mode-to", "<yellow>Switch to survival mode to harvest with the farm hoe.")));return;}
        if(!hasTool(player)&&inFarm(player))equip(player,false);
        player.sendActionBar(Text.mm(hasTool(player)?"<yellow>Hold your farm hoe and left-click mature wheat.":"<yellow>Stand inside the field to get your farm hoe."));
    }
    private final Map<UUID,Long> hints=new java.util.concurrent.ConcurrentHashMap<>();
    public boolean equip(Player player){return equip(player,true);}
    /** @param select also switch the hotbar to the hoe (on entering the field, not on a hint) */
    public boolean equip(Player player,boolean select){
        var data=plugin.questManager().data(player);
        // The first tool is free: hand it out on the way in instead of making players find the anvil first.
        Tier first=tiers.get(1);
        if(data.hoeTier()==0&&first!=null&&first.cost()<=0&&plugin.progression().level(data)>=first.level()&&inFarm(player)){
            data.setHoeTier(1);plugin.send(player,T.t("farm-service.you-got-a-free-left", "<green>You got a free <name><gray>. Left-click mature wheat to harvest it; it regrows in a second.", "name", Text.escape(first.name())));
        }
        Tier tier=tiers.get(data.hoeTier());
        if(tier==null||!inFarm(player))return false;
        strip(player);
        int slot=-1;
        for(int i=0;i<9;i++){ItemStack stack=player.getInventory().getItem(i);if(stack==null||stack.getType().isAir()){slot=i;break;}}
        if(slot<0){plugin.send(player,T.t("farm-service.make-room-in-your-hotbar", "<yellow>Make room in your hotbar, then use the field locker."));return false;}
        player.getInventory().setItem(slot,tool(player,tier));
        if(select&&slot<9)player.getInventory().setHeldItemSlot(slot);
        return true;
    }
    public boolean purchase(Player player,int id){
        Tier tier=tiers.get(id);var data=plugin.questManager().data(player);
        if(tier==null||id!=data.hoeTier()+1){plugin.send(player,T.t("farm-service.upgrades-follow-the-tool-tiers", "<yellow>Upgrades follow the tool tiers in order."));return false;}
        if(plugin.progression().level(data)<tier.level()){plugin.send(player,T.t("farm-service.wayfarer-level-is-required", "<red>Wayfarer level <level> is required.", "level", tier.level()));return false;}
        if(tier.cost()>0&&!economy.available()){plugin.send(player,T.t("farm-service.the-economy-provider-is-unavailable", "<red>The economy provider is unavailable. No money was taken."));return false;}
        if(!economy.withdraw(player,tier.cost())){plugin.send(player,T.t("farm-service.purchase-declined-check-your-balance", "<red>Purchase declined. Check your balance or economy provider."));return false;}
        data.setHoeTier(id);plugin.store().saveNow(data);strip(player);if(inFarm(player))equip(player);
        player.playSound(player.getLocation(),Sound.BLOCK_ANVIL_USE,.5f,1.3f);
        plugin.send(player,T.t("farm-service.unlocked-stored-in-your-personal", "<green>Unlocked <name><gray>. Stored in your personal locker.", "name", Text.escape(tier.name())));
        return true;
    }
    /** Keep dry soil intact only during an accepted crop's regrowth gap. */
    public boolean pendingRegrowth(Location crop){
        return running&&pending.contains(new Spot(crop.getWorld().getName(),crop.getBlockX(),crop.getBlockY(),crop.getBlockZ()));
    }
    /** Triggered only for one block; even high-tier tools never harvest neighbors. */
    public void harvest(Player player,Block block){
        if(player.getGameMode()==GameMode.CREATIVE&&area(block.getLocation())!=null){hint(player);return;}
        if(!player.isOnline()||player.getGameMode()==GameMode.SPECTATOR||player.getGameMode()==GameMode.CREATIVE
                ||!player.getWorld().equals(block.getWorld())||player.getEyeLocation().distanceSquared(block.getLocation().add(.5,.5,.5))>36)return;
        ItemStack held=player.getInventory().getItemInMainHand();
        if(!owned(player,held)||!inFarm(player)||area(block.getLocation())==null)return;
        Tier tier=tiers.get(plugin.questManager().data(player).hoeTier());if(tier==null)return;
        long now=System.nanoTime(),due=cooldowns.getOrDefault(player.getUniqueId(),0L);
        if(now<due)return;cooldowns.put(player.getUniqueId(),now+tier.cooldown()*50_000_000L);
        Spot spot=new Spot(block.getWorld().getName(),block.getX(),block.getY(),block.getZ());
        Sched.at(block.getLocation(),()->{
            if(!running||block.getType()!=Material.WHEAT||!(block.getBlockData() instanceof Ageable age)
                    ||age.getAge()!=age.getMaximumAge()||area(block.getLocation())==null||!pending.add(spot))return;
            block.setType(Material.AIR,false);
            if(particles){block.getWorld().spawnParticle(Particle.COMPOSTER,block.getLocation().add(.5,.4,.5),6,.25,.25,.25,0);
                block.getWorld().spawnParticle(Particle.BLOCK,block.getLocation().add(.5,.3,.5),8,.2,.2,.2,0,age);}
            Sched.entity(player,()->{
                if(!running)return;
                var data=plugin.questManager().data(player);data.addWheat(1);
                plugin.mail().discovered(player);
                int wheat=ThreadLocalRandom.current().nextDouble()<tier.chance()?2:1;
                player.getInventory().addItem(new ItemStack(Material.WHEAT,wheat)); // full bags don't create farm-item drops
                plugin.questManager().progressFromFarm(player,"WHEAT");
                plugin.progression().award(player,Math.max(1,Math.round(xp*tier.multiplier())),true);
            });
            Bukkit.getRegionScheduler().runDelayed(plugin,block.getLocation(),t->regrow(spot),regrow);
        });
    }
    private void regrow(Spot spot){
        Location loc=spot.location();if(loc==null)return;
        if(!loc.getWorld().isChunkLoaded(spot.x()>>4,spot.z()>>4))return;
        Block block=loc.getBlock();
        if(area(loc)!=null&&block.getType()==Material.AIR&&block.getRelative(0,-1,0).getType()==Material.FARMLAND){
            Ageable age=(Ageable)Material.WHEAT.createBlockData();age.setAge(age.getMaximumAge());block.setBlockData(age,false);
        }
        pending.remove(spot);
    }
    public void restoreLoaded(){for(Spot s:pending){Location l=s.location();if(l!=null&&l.getWorld().isChunkLoaded(s.x()>>4,s.z()>>4))Sched.at(l,()->regrow(s));}}
    public void restoreChunk(World world,int x,int z){for(Spot s:pending)if(s.world().equals(world.getName())&&(s.x()>>4)==x&&(s.z()>>4)==z)Sched.at(new Location(world,s.x(),s.y(),s.z()),()->regrow(s));}
    public synchronized void savePending(){
        Set<Spot> snapshot=Set.copyOf(pending);
        if(!writer.isShutdown())writer.execute(()->{
            if(snapshot.equals(savedPending))return;
            var yaml=new YamlConfiguration();yaml.set("pending",snapshot.stream().map(Spot::encode).toList());
            try{Path tmp=pendingFile.toPath().resolveSibling("farm-regrowth.yml.tmp");Files.writeString(tmp,yaml.saveToString());
                try{Files.move(tmp,pendingFile.toPath(),StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);}
                catch(AtomicMoveNotSupportedException e){Files.move(tmp,pendingFile.toPath(),StandardCopyOption.REPLACE_EXISTING);}
                savedPending=snapshot;
            }catch(Exception e){plugin.getLogger().warning("Farm regrowth save failed: "+e.getMessage());}
        });
    }
    public synchronized void saveArea(String id,String world,String region,Polygon outline,boolean outside,int[] bounds){
        String p="areas."+id+".";
        config.set(p+"world",world);config.set(p+"region",region);config.set(p+"outside",outside);
        config.set(p+"vertices",outline.vertices().stream().map(v->v.x()+","+v.z()).toList());
        config.set(p+"bounds",Arrays.stream(bounds).boxed().toList());
        saveConfig();reload();
    }
    private static Spot spot(Location loc){return new Spot(loc.getWorld().getName(),loc.getBlockX(),loc.getBlockY(),loc.getBlockZ());}
    private Set<Spot> readUpgraders(){var result=new HashSet<Spot>();for(String value:config.getStringList("upgraders")){var point=Spot.decode(value);if(point!=null)result.add(point);}var old=Spot.decode(config.getString("upgrader",""));if(old!=null)result.add(old);return Set.copyOf(result);}
    public synchronized void setUpgrader(Location loc){config.set("upgrader",spot(loc).encode());saveConfig();upgraders=readUpgraders();}
    public synchronized void addUpgrader(Location loc){var next=new HashSet<>(upgraders);next.add(spot(loc));config.set("upgraders",next.stream().map(Spot::encode).sorted().toList());saveConfig();upgraders=Set.copyOf(next);}
    public synchronized void removeUpgrader(Location loc){var point=spot(loc);var next=new HashSet<>(upgraders);if(!next.remove(point))return;upgraders=Set.copyOf(next);config.set("upgraders",next.stream().map(Spot::encode).sorted().toList());if(point.encode().equals(config.getString("upgrader")))config.set("upgrader",null);saveConfig();}
    public boolean registeredUpgrader(Location loc){return upgraders.contains(spot(loc));}
    public boolean upgrader(Block b){return b!=null&&switch(b.getType()){case ANVIL,CHIPPED_ANVIL,DAMAGED_ANVIL->registeredUpgrader(b.getLocation());default->false;};}
    public boolean validUpgrader(Player player,Spot point){if(point==null||!upgraders.contains(point)||!point.world().equals(player.getWorld().getName()))return false;var at=player.getEyeLocation();double x=at.getX()-point.x()-.5,y=at.getY()-point.y()-.5,z=at.getZ()-point.z()-.5;return x*x+y*y+z*z<=36;}
    public Spot nearbyUpgrader(Player player){for(var point:upgraders)if(validUpgrader(player,point))return point;return null;}
    public boolean anvilItem(ItemStack item){return item!=null&&item.getType()==Material.ANVIL&&item.hasItemMeta()&&item.getItemMeta().getPersistentDataContainer().has(anvilKey,PersistentDataType.BYTE);}
    public ItemStack anvilItem(){var item=new ItemStack(Material.ANVIL);item.editMeta(meta->{meta.displayName(Text.mm(T.t("farm-service.fieldsmith-anvil", "<!italic><gold><bold>Fieldsmith Anvil")));meta.lore(List.of(Text.mm(T.t("farm-service.op-place-on-solid-ground", "<gray>OP: place on solid ground to create a workshop.")),Text.mm(T.t("farm-service.players-right-click-to-upgrade", "<yellow>Players: right-click to upgrade your hoe."))));meta.getPersistentDataContainer().set(anvilKey,PersistentDataType.BYTE,(byte)1);});return item;}
    public String role(String npc){for(String role:List.of("shop","upgrader","locker"))if(npc.equalsIgnoreCase(config.getString("npcs."+role,"")))return role;return null;}
    private void saveConfig(){try{config.save(file);}catch(Exception e){throw new IllegalStateException("Farm configuration could not be saved",e);}}
    public synchronized void shutdown(){running=false;savePending();writer.shutdown();try{if(!writer.awaitTermination(10,TimeUnit.SECONDS))plugin.getLogger().warning("Farm writer did not drain within 10 seconds");}catch(InterruptedException e){Thread.currentThread().interrupt();}}
    public void forget(Player p){strip(p);inside.remove(p.getUniqueId());hints.remove(p.getUniqueId());cooldowns.remove(p.getUniqueId());}
}
