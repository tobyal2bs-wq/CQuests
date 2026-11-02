package com.cquests.farm;

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
    private final NamespacedKey hoeKey,ownerKey,tierKey;
    private final Map<UUID,Long> cooldowns=new ConcurrentHashMap<>();
    private final Set<UUID> inside=ConcurrentHashMap.newKeySet();
    private final Set<Spot> pending=ConcurrentHashMap.newKeySet();
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
        reload();
        for(String s:YamlConfiguration.loadConfiguration(pendingFile).getStringList("pending")){
            Spot spot=Spot.decode(s);if(spot!=null)pending.add(spot);
        }
        restoreLoaded();
    }
    public void reload(){
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
        areas=List.copyOf(list);economy.refresh();
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
            meta.lore(List.of(Text.mm("<!italic><gray>Personal farm tool • wheat only"),
                    Text.mm("<!italic><aqua>Skill XP ×"+tier.multiplier()+" <gray>• extra wheat "+Math.round(tier.chance()*100)+"%"),
                    Text.mm("<!italic><gray>Returns to your private locker when you leave.")));
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
        boolean isInside=inFarm(player);
        if(isInside){
            boolean entered=inside.add(player.getUniqueId());
            if(entered){plugin.send(player,"<gold>Harvest grounds <gray>• commands are paused; your tool is bound to this area.");equip(player);}
            if(!entered&&!auditInventory)return;
            int count=0;boolean invalid=marked(player.getItemOnCursor());
            for(ItemStack item:player.getInventory().getContents())if(marked(item)){count+=item.getAmount();invalid|=!owned(player,item);}
            if(invalid||count>1){strip(player);equip(player);}
        }else if(inside.remove(player.getUniqueId())||(auditInventory&&hasTool(player))){
            strip(player);cooldowns.remove(player.getUniqueId());
            player.sendActionBar(Text.mm("<gray>Your hoe is safe in your private field locker."));
        }
    }
    private boolean hasTool(Player player){for(ItemStack item:player.getInventory().getContents())if(marked(item))return true;return marked(player.getItemOnCursor());}
    public void strip(Player player){
        for(int i=0;i<player.getInventory().getSize();i++)if(marked(player.getInventory().getItem(i)))player.getInventory().setItem(i,null);
        if(marked(player.getItemOnCursor()))player.setItemOnCursor(null);
    }
    public boolean equip(Player player){
        var data=plugin.questManager().data(player);Tier tier=tiers.get(data.hoeTier());
        if(tier==null||!inFarm(player))return false;
        strip(player);
        int slot=-1;
        for(int i=0;i<9;i++){ItemStack stack=player.getInventory().getItem(i);if(stack==null||stack.getType().isAir()){slot=i;break;}}
        if(slot<0){plugin.send(player,"<yellow>Make room in your hotbar, then use the field locker.");return false;}
        player.getInventory().setItem(slot,tool(player,tier));
        if(slot<9)player.getInventory().setHeldItemSlot(slot);
        return true;
    }
    public boolean purchase(Player player,int id){
        Tier tier=tiers.get(id);var data=plugin.questManager().data(player);
        if(tier==null||id!=data.hoeTier()+1){plugin.send(player,"<yellow>Upgrades follow the tool tiers in order.");return false;}
        if(plugin.progression().level(data)<tier.level()){plugin.send(player,"<red>Wayfarer level "+tier.level()+" is required.");return false;}
        if(tier.cost()>0&&!economy.available()){plugin.send(player,"<red>The economy provider is unavailable. No money was taken.");return false;}
        if(!economy.withdraw(player,tier.cost())){plugin.send(player,"<red>Purchase declined. Check your balance or economy provider.");return false;}
        data.setHoeTier(id);plugin.store().saveNow(data);strip(player);if(inFarm(player))equip(player);
        player.playSound(player.getLocation(),Sound.BLOCK_ANVIL_USE,.5f,1.3f);
        plugin.send(player,"<green>Unlocked "+Text.escape(tier.name())+"<gray>. Stored in your personal locker.");
        return true;
    }
    /** Keep dry soil intact only during an accepted crop's regrowth gap. */
    public boolean pendingRegrowth(Location crop){
        return running&&pending.contains(new Spot(crop.getWorld().getName(),crop.getBlockX(),crop.getBlockY(),crop.getBlockZ()));
    }
    /** Triggered only for one block; even high-tier tools never harvest neighbors. */
    public void harvest(Player player,Block block){
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
                plugin.questManager().progress(player,ObjectiveType.HARVEST,"WHEAT",1);
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
        List<String> points=pending.stream().map(Spot::encode).toList();
        if(!writer.isShutdown())writer.execute(()->{
            var yaml=new YamlConfiguration();yaml.set("pending",points);
            try{Path tmp=pendingFile.toPath().resolveSibling("farm-regrowth.yml.tmp");Files.writeString(tmp,yaml.saveToString());
                try{Files.move(tmp,pendingFile.toPath(),StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);}
                catch(AtomicMoveNotSupportedException e){Files.move(tmp,pendingFile.toPath(),StandardCopyOption.REPLACE_EXISTING);}
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
    public synchronized void setUpgrader(Location loc){config.set("upgrader",new Spot(loc.getWorld().getName(),loc.getBlockX(),loc.getBlockY(),loc.getBlockZ()).encode());saveConfig();}
    public boolean upgrader(Block b){return new Spot(b.getWorld().getName(),b.getX(),b.getY(),b.getZ()).encode().equals(config.getString("upgrader"));}
    public String role(String npc){for(String role:List.of("shop","upgrader","locker"))if(npc.equalsIgnoreCase(config.getString("npcs."+role,"")))return role;return null;}
    private void saveConfig(){try{config.save(file);}catch(Exception e){throw new IllegalStateException("Farm configuration could not be saved",e);}}
    public synchronized void shutdown(){running=false;savePending();writer.shutdown();try{if(!writer.awaitTermination(10,TimeUnit.SECONDS))plugin.getLogger().warning("Farm writer did not drain within 10 seconds");}catch(InterruptedException e){Thread.currentThread().interrupt();}}
    public void forget(Player p){strip(p);inside.remove(p.getUniqueId());cooldowns.remove(p.getUniqueId());}
}
