package com.cbosses.friendly;

import com.cbosses.CBossesPlugin;
import com.cbosses.model.BossModel;
import com.cbosses.model.ModelRig;
import org.bukkit.*;
import org.bukkit.command.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.player.PlayerInteractEntityEvent;
import org.bukkit.event.entity.EntityDamageEvent;
import org.bukkit.event.player.PlayerTeleportEvent.TeleportCause;
import org.bukkit.persistence.PersistentDataType;
import io.papermc.paper.entity.TeleportFlag;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ThreadLocalRandom;

/** Independent peaceful Mossbacks. No targeting, attacks, arena or boss timer. */
public final class FriendlyMossbacks implements Listener, CommandExecutor, TabCompleter {
    private final CBossesPlugin plugin;
    private final NamespacedKey kind, fight, friendly;
    private final Map<UUID, Pet> pets = new ConcurrentHashMap<>();
    private volatile boolean stopping;
    private final Map<UUID, Location> homes = new ConcurrentHashMap<>();
    private final Set<UUID> waking = ConcurrentHashMap.newKeySet();
    private io.papermc.paper.threadedregions.scheduler.ScheduledTask wakeLoop;
    private static final class Pet {
        UUID id; Pig carrier; ArmorStand seat; BossModel model;
        float yaw; int ticks; volatile boolean movingSeat, movingCarrier, deleted;
        volatile Location last;
    }
    public FriendlyMossbacks(CBossesPlugin plugin) {
        this.plugin=plugin; kind=new NamespacedKey(plugin,"boss");
        fight=new NamespacedKey(plugin,"fight"); friendly=new NamespacedKey(plugin,"friendly-mossback");
    }
    public void start() {
        var file = new java.io.File(plugin.getDataFolder(),"friendly-mossbacks.yml");
        var yaml=org.bukkit.configuration.file.YamlConfiguration.loadConfiguration(file);
        var section=yaml.getConfigurationSection("mossbacks");
        if(section!=null) for(String id:section.getKeys(false)) {
            String base="mossbacks."+id;World w=Bukkit.getWorld(yaml.getString(base+".world",""));
            if(w==null)continue;
            Location at=new Location(w,yaml.getDouble(base+".x"),yaml.getDouble(base+".y"),yaml.getDouble(base+".z"),(float)yaml.getDouble(base+".yaw"),0);
            try {homes.put(UUID.fromString(id),at);} catch(IllegalArgumentException ignored) { }
        }
        wakeLoop=Bukkit.getGlobalRegionScheduler().runAtFixedRate(plugin,t->{
            for(var entry:homes.entrySet()) {
                UUID id=entry.getKey();Location at=entry.getValue();
                if(pets.containsKey(id) || !at.getWorld().isChunkLoaded(at.getBlockX()>>4,at.getBlockZ()>>4) || !waking.add(id))continue;
                Bukkit.getRegionScheduler().execute(plugin,at,()->{
                    try {if(!stopping && homes.containsKey(id) && !pets.containsKey(id))spawn(id,at);}
                    finally {waking.remove(id);}
                });
            }
        },40,40);
    }
    private synchronized void save() {
        var yaml=new org.bukkit.configuration.file.YamlConfiguration();
        for(var entry:pets.entrySet()) if(entry.getValue().last!=null) homes.put(entry.getKey(),entry.getValue().last);
        for(var entry:homes.entrySet()) {
            Location at=entry.getValue();
            String path="mossbacks."+entry.getKey();
            yaml.set(path+".world",at.getWorld().getName());yaml.set(path+".x",at.getX());yaml.set(path+".y",at.getY());yaml.set(path+".z",at.getZ());yaml.set(path+".yaw",at.getYaw());
        }
        try { com.cbosses.util.SafeFiles.write(new java.io.File(plugin.getDataFolder(),"friendly-mossbacks.yml"),yaml.saveToString()); }
        catch(java.io.IOException e) {plugin.getLogger().warning("Could not save friendly Mossbacks: "+e.getMessage());}
    }
    @Override public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (!sender.hasPermission("bosses.use")) { sender.sendMessage("You cannot spawn Mossbacks.");return true; }
        if (args.length==0) { sender.sendMessage("/mossback spawn [x y z [world]] | remove | list");return true; }
        if (args[0].equalsIgnoreCase("list")) { sender.sendMessage("Friendly Mossbacks: "+homes.size());return true; }
        if (args[0].equalsIgnoreCase("remove") && sender instanceof Player p) {
            Pet nearest=pets.values().stream().filter(pet->pet.carrier.getWorld().equals(p.getWorld()) && Bukkit.isOwnedByCurrentRegion(pet.carrier))
                    .filter(pet->pet.carrier.getLocation().distanceSquared(p.getLocation())<144)
                    .min(Comparator.comparingDouble(pet->pet.carrier.getLocation().distanceSquared(p.getLocation()))).orElse(null);
            if(nearest!=null) { remove(nearest);sender.sendMessage("Removed the nearest friendly Mossback."); }
            else sender.sendMessage("No friendly Mossback within 12 blocks.");
            return true;
        }
        if (!args[0].equalsIgnoreCase("spawn")) return true;
        Location at=sender instanceof Player p?p.getLocation().clone():null;
        try {
            if(args.length>=4) {
                World world=args.length>=5?Bukkit.getWorld(args[4]):at==null?null:at.getWorld();
                if(world==null) throw new IllegalArgumentException();
                at=new Location(world,Double.parseDouble(args[1]),Double.parseDouble(args[2]),Double.parseDouble(args[3]));
            }
            if(at==null || !Double.isFinite(at.getX()) || !Double.isFinite(at.getY()) || !Double.isFinite(at.getZ())
                    || Math.abs(at.getX())>29999900 || Math.abs(at.getZ())>29999900) throw new IllegalArgumentException();
        } catch(IllegalArgumentException e) {sender.sendMessage("Use /mossback spawn x y z world, or /mossback spawn at your feet.");return true;}
        Location spawn=at;
        spawn.getWorld().getChunkAtAsync(spawn).thenRun(()->Bukkit.getRegionScheduler().execute(plugin,spawn,()->{
            spawn(spawn);sender.sendMessage("Spawned a friendly Mossback. Right-click to ride; sneak to leave.");
        }));
        return true;
    }
    public void spawn(Location at) { spawn(UUID.randomUUID(),at); }
    private void spawn(UUID id, Location at) {
        ModelRig.Model rig=plugin.service().model("mossback");
        if(rig==null) throw new IllegalStateException("Mossback model missing");
        Pet pet=new Pet();pet.id=id;pet.yaw=at.getYaw();pet.last=at.clone();homes.put(id,at.clone());
        pet.carrier=at.getWorld().spawn(at,Pig.class,p->{
            p.setAdult();p.setAgeLock(true);p.setAI(false);p.setInvisible(true);p.setSilent(true);
            p.setInvulnerable(true);p.setCollidable(false);p.setPersistent(false);p.setGravity(false);
            p.getPersistentDataContainer().set(friendly,PersistentDataType.STRING,id.toString());
            var step=Registry.ATTRIBUTE.get(NamespacedKey.minecraft("step_height"));
            if(step!=null && p.getAttribute(step)!=null) p.getAttribute(step).setBaseValue(0);
        });
        pets.put(id,pet);
        pet.model=new BossModel(plugin,rig,pet.carrier);
        pet.model.build(kind,fight,"friendly:"+id);
        pet.seat=at.getWorld().spawn(seatAt(pet),ArmorStand.class,s->{
            s.setVisible(false);s.setMarker(true);s.setGravity(false);s.setInvulnerable(true);s.setSilent(true);s.setPersistent(false);
            s.getPersistentDataContainer().set(friendly,PersistentDataType.STRING,id.toString());
        });
        pet.model.appear(()->{});
        if(!stopping)save();
        pet.carrier.getScheduler().runAtFixedRate(plugin,t->{
            if(!pet.carrier.isValid() || !pet.seat.isValid()) { t.cancel();retire(pet);return; }
            tick(pet);
        },()->retire(pet),5,5);
    }
    private Location seatAt(Pet pet) {
        float s=pet.model.model.scale/16f;
        // Front of the shell, ahead of the ruined tower, facing the head.
        double a=Math.toRadians(pet.yaw), z=8*s;
        return pet.carrier.getLocation().add(-Math.sin(a)*z,17*s,Math.cos(a)*z);
    }
    private void tick(Pet pet) {
        pet.ticks+=5;
        Location at=pet.carrier.getLocation();
        pet.last=at.clone();
        if(pet.ticks%80==0) pet.yaw+=ThreadLocalRandom.current().nextFloat()*100-50;
        pet.carrier.setRotation(pet.yaw,0);
        double a=Math.toRadians(pet.yaw), dx=-Math.sin(a)*0.055,dz=Math.cos(a)*0.055;
        // Check the whole body footprint, including a look-ahead margin. Never
        // load chunks or inspect blocks owned by a different Folia region.
        double radius=Math.max(.5,pet.model.model.blocks()*.30);
        boolean allowed=pet.ticks%140<105;
        for(double x:new double[]{-radius,0,radius}) for(double z:new double[]{-radius,0,radius}) {
            Location spot=at.clone().add(x+dx*12,-.05,z+dz*12);
            if(!Bukkit.isOwnedByCurrentRegion(spot) || !spot.getWorld().isChunkLoaded(spot.getBlockX()>>4,spot.getBlockZ()>>4)) {allowed=false;continue;}
            if(spot.getBlock().getType()!=Material.DIRT) allowed=false;
            for(int y=1;y<=Math.ceil(pet.model.model.blocks());y++)
                if(!spot.clone().add(0,y,0).getBlock().isPassable())allowed=false;
        }
        if(allowed && !pet.movingCarrier) {
            pet.movingCarrier=true;
            Location next=at.clone().add(dx*5,0,dz*5);next.setYaw(pet.yaw);next.setPitch(0);
            pet.carrier.teleportAsync(next,TeleportCause.PLUGIN,TeleportFlag.EntityState.RETAIN_PASSENGERS)
                    .whenComplete((ok,error)->pet.movingCarrier=false);
        }
        if(!allowed && pet.ticks%20==0) pet.yaw+=65;
        Location seat=seatAt(pet);seat.setYaw(pet.yaw);seat.setPitch(0);
        if(!pet.movingSeat) {
            pet.movingSeat=true;
            pet.seat.getScheduler().run(plugin,t->pet.seat.teleportAsync(seat,TeleportCause.PLUGIN,TeleportFlag.EntityState.RETAIN_PASSENGERS)
                    .whenComplete((ok,error)->pet.movingSeat=false),()->pet.movingSeat=false);
        }
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void ride(PlayerInteractEntityEvent event) {
        Entity clicked=event.getRightClicked();String id=clicked.getPersistentDataContainer().get(friendly,PersistentDataType.STRING);
        if(id==null) {
            String tag=clicked.getPersistentDataContainer().get(fight,PersistentDataType.STRING);
            if(tag!=null && tag.startsWith("friendly:")) id=tag.substring(9);
        }
        if(id==null)return;
        Pet pet;try{pet=pets.get(UUID.fromString(id));}catch(IllegalArgumentException e){return;}
        if(pet==null)return;event.setCancelled(true);
        if(event.getHand()!=org.bukkit.inventory.EquipmentSlot.HAND)return;
        Player player=event.getPlayer();
        if(!Bukkit.isOwnedByCurrentRegion(pet.seat) || player.isInsideVehicle())return;
        if(pet.seat.getPassengers().isEmpty())pet.seat.addPassenger(player);
        else player.sendMessage("Someone is already riding this Mossback.");
    }
    @EventHandler(ignoreCancelled=true) public void protect(EntityDamageEvent event) {
        String tag=event.getEntity().getPersistentDataContainer().get(fight,PersistentDataType.STRING);
        if(event.getEntity().getPersistentDataContainer().has(friendly,PersistentDataType.STRING)
                || tag!=null && tag.startsWith("friendly:"))event.setCancelled(true);
    }
    private void remove(Pet pet) { pet.deleted=true; homes.remove(pet.id); despawn(pet); if(!stopping)save(); }
    private void retire(Pet pet) { if(!pet.deleted && !stopping && pet.last!=null)homes.put(pet.id,pet.last);despawn(pet); }
    private void despawn(Pet pet) {
        pets.remove(pet.id);pet.model.remove();
        for(Entity entity:new Entity[]{pet.seat,pet.carrier}) if(entity!=null && entity.isValid()) {
            if(Bukkit.isOwnedByCurrentRegion(entity))entity.remove();
            else entity.getScheduler().run(plugin,t->entity.remove(),null);
        }
    }
    public void stop(){
        stopping=true;if(wakeLoop!=null)wakeLoop.cancel();save();
        // Folia halts region tick contexts before disabling plugins. Removing
        // entities then can dereference missing region data on 26.2. These
        // entities are nonpersistent; the server discards them during unload.
        if(Bukkit.isStopping()){pets.clear();return;}
        for(Pet pet:List.copyOf(pets.values()))despawn(pet);
    }
    @Override public List<String> onTabComplete(CommandSender s,Command c,String a,String[] args){
        return args.length==1?List.of("spawn","remove","list").stream().filter(x->x.startsWith(args[0].toLowerCase(Locale.ROOT))).toList():List.of();
    }
}
