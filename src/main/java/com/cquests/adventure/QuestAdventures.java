package com.cquests.adventure;

import com.cquests.CQuestsPlugin;
import com.cquests.gui.LockedMenu;
import com.cquests.gui.QuestMenu;
import com.cquests.model.*;
import com.cquests.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.entity.*;
import org.bukkit.event.player.*;
import org.bukkit.event.vehicle.VehicleEnterEvent;
import org.bukkit.event.world.EntitiesLoadEvent;
import org.bukkit.inventory.Inventory;
import org.bukkit.event.inventory.ClickType;
import org.bukkit.persistence.PersistentDataType;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/** Small, player-owned encounters. Entity work stays on its owner scheduler. */
public final class QuestAdventures implements Listener {
    public static final String BOSS_QUEST="story_aldis";
    private static final Set<String> ESCORTS=Set.of("story_martha","story_iona");
    private static final class Session {
        final Player player;final String quest;final Mob mob;
        final long born=System.nanoTime();final Location origin;
        volatile Location playerAt;volatile boolean active=true;
        volatile Location helperAt;
        final java.util.concurrent.atomic.AtomicBoolean released=new java.util.concurrent.atomic.AtomicBoolean();
        Session(Player player,String quest,Mob mob){this.player=player;this.quest=quest;this.mob=mob;origin=mob.getLocation();helperAt=origin;playerAt=player.getLocation();}
    }
    private final CQuestsPlugin plugin;
    private final NamespacedKey ownerKey,kindKey;
    private final Map<UUID,Session> companions=new ConcurrentHashMap<>(),bosses=new ConcurrentHashMap<>();
    private final Map<UUID,Long> retry=new ConcurrentHashMap<>();
    private final java.util.concurrent.Semaphore helperSlots=new java.util.concurrent.Semaphore(32),bossSlots=new java.util.concurrent.Semaphore(4);
    private volatile boolean running=true;
    public QuestAdventures(CQuestsPlugin plugin){this.plugin=plugin;ownerKey=new NamespacedKey(plugin,"adventure_owner");kindKey=new NamespacedKey(plugin,"adventure_kind");}
    public boolean marked(Entity entity){return entity.getPersistentDataContainer().has(ownerKey,PersistentDataType.STRING);}
    public UUID owner(Entity entity){
        String id=entity.getPersistentDataContainer().get(ownerKey,PersistentDataType.STRING);
        try{return id==null?null:UUID.fromString(id);}catch(IllegalArgumentException ignored){return null;}
    }
    private void mark(Entity entity,Player player,String kind){
        entity.getPersistentDataContainer().set(ownerKey,PersistentDataType.STRING,player.getUniqueId().toString());
        entity.getPersistentDataContainer().set(kindKey,PersistentDataType.STRING,kind);entity.setPersistent(false);
    }
    private boolean playable(Player player){return player.isOnline()&&!player.isDead()&&(player.getGameMode()==GameMode.SURVIVAL||player.getGameMode()==GameMode.ADVENTURE);}
    private boolean active(Player player,String quest){
        var q=plugin.quests().get(quest);var a=plugin.questManager().data(player).active(quest);
        return q!=null&&a!=null&&!plugin.questManager().ready(q,a);
    }
    /** Called by the existing player ticker; publishes locations, never reads a remote mob's location. */
    public void update(Player player){
        UUID id=player.getUniqueId();if(!running||!plugin.getConfig().getBoolean("adventures.enabled",true))return;
        Session boss=bosses.get(id),helper=companions.get(id);
        if(boss!=null){if(!playable(player)||!active(player,boss.quest)||!same(boss.origin,player.getLocation(),48))stop(bosses,id,boss);else boss.playerAt=player.getLocation();}
        if(helper!=null){if(!playable(player)||!active(player,helper.quest)||!helper.origin.getWorld().equals(player.getWorld()))stop(companions,id,helper);else helper.playerAt=player.getLocation();return;}
        if(!plugin.getConfig().getBoolean("adventures.companions",true)||!playable(player)||companions.size()>=32||System.nanoTime()<retry.getOrDefault(id,0L))return;
        for(String quest:ESCORTS)if(active(player,quest)){
            retry.put(id,System.nanoTime()+10_000_000_000L);
            Location at=ground(player.getLocation(),2);if(at==null)return;
            if(!helperSlots.tryAcquire())return;
            Villager villager;
            try{villager=at.getWorld().spawn(at,Villager.class,v->{
                mark(v,player,"companion");v.customName(null);
                v.setCustomNameVisible(false);v.setInvulnerable(true);v.setCollidable(false);v.setSilent(true);v.setVisibleByDefault(false);
                v.setRemoveWhenFarAway(false);v.setCanPickupItems(false);v.setProfession(Villager.Profession.WEAPONSMITH);v.setAdult();v.setBreed(false);
            });}catch(RuntimeException error){helperSlots.release();plugin.getLogger().warning("Companion spawn declined: "+error.getMessage());return;}
            if(!villager.isValid()){helperSlots.release();return;}
            var session=new Session(player,quest,villager);companions.put(id,session);player.showEntity(plugin,villager);
            String label="companion_"+id;
            plugin.nameplates().spawn(new NpcDef(label,"<gold>Pip</gold>","Your companion","WEAPONSMITH","PLAINS",
                    plugin.progression().level(plugin.questManager().data(player)),1,true,false,false,"",List.of(),List.of()),villager,at);
            plugin.nameplates().show(player,label,true);
            plugin.send(player,"<gold>Pip <gray>jogs up beside you. <white>I'll watch your back. You take the lead.");
            villager.getScheduler().runAtFixedRate(plugin,t->{if(!tick(session,false)){t.cancel();return;}},()->retired(companions,id,session),5,5);
            return;
        }
    }
    private static boolean same(Location a,Location b,double radius){return a.getWorld().equals(b.getWorld())&&a.distanceSquared(b)<=radius*radius;}
    private Location ground(Location from,int offset){
        Location at=from.clone().add(offset,0,0);
        for(int dy:new int[]{0,1,-1}){
            var loc=at.clone().add(0,dy,0);if(!Bukkit.isOwnedByCurrentRegion(loc))continue;
            var b=loc.getBlock();var floor=b.getRelative(0,-1,0);
            if(b.getType().isAir()&&b.getRelative(0,1,0).getType().isAir()&&floor.getType().isSolid()
                    &&!Set.of(Material.MAGMA_BLOCK,Material.CAMPFIRE,Material.SOUL_CAMPFIRE,Material.CACTUS).contains(floor.getType()))return b.getLocation().add(.5,0,.5);
        }
        return null;
    }
    private boolean tick(Session session,boolean boss){
        Mob mob=session.mob;UUID id=session.player.getUniqueId();var sessions=boss?bosses:companions;
        if(!running||!session.active||sessions.get(id)!=session||!mob.isValid()){retired(sessions,id,session);if(mob.isValid())mob.remove();return false;}
        Location target=session.playerAt;
        if(System.nanoTime()-session.born>600_000_000_000L||!same(mob.getLocation(),target,boss?56:24)){
            stop(sessions,id,session);return false;
        }
        if(boss){
            // Folia requires both entities to belong to this region before setting a live target.
            if(Bukkit.isOwnedByCurrentRegion(session.player))for(var head:Wither.Head.values())((Wither)mob).setTarget(head,session.player);
            else {stop(sessions,id,session);return false;}
        }else{
            session.helperAt=mob.getLocation();
            plugin.nameplates().follow("companion_"+id,session.helperAt);
            var villager=(Villager)mob;
            if(mob.getLocation().distanceSquared(target)>6.25)villager.getPathfinder().moveTo(target,1.15);
            else villager.getPathfinder().stopPathfinding();
        }
        return true;
    }
    public boolean offerBoss(Player player,NpcDef npc){
        if(!npc.id().equals("aldis")||!active(player,BOSS_QUEST))return false;
        Inventory inv=Bukkit.createInventory(new BossMenu(player),27,Text.mm("<dark_gray>The Hollow King's vessel"));
        var menu=(BossMenu)inv.getHolder();menu.inventory=inv;
        for(int i=0;i<27;i++)inv.setItem(i,QuestMenu.item(Material.BLACK_STAINED_GLASS_PANE," ",List.of()));
        inv.setItem(13,QuestMenu.item(Material.WITHER_SKELETON_SKULL,"<gold><bold>Face the vessel",List.of(
                "<white>The Wither will hunt you alone.","<gray>Other players cannot fight it for you.","<gray>Leave the area or fall, and it withdraws.","<yellow>Click when you are ready.")));
        inv.setItem(26,QuestMenu.item(Material.BARRIER,"<gray>Not yet",List.of()));player.openInventory(inv);return true;
    }
    public boolean summon(Player player){
        UUID id=player.getUniqueId();
        if(player.getWorld().getDifficulty()==Difficulty.PEACEFUL){plugin.send(player,"<yellow>The vessel cannot wake in a Peaceful world.");return false;}
        if(!running||!plugin.getConfig().getBoolean("adventures.enabled",true)||!plugin.getConfig().getBoolean("adventures.wither",true)
                ||!playable(player)||!active(player,BOSS_QUEST)||bosses.containsKey(id)||bosses.size()>=4)return false;
        Location at=ground(player.getLocation(),6);
        if(at==null){plugin.send(player,"<yellow>Find clear, solid ground with space beside you before summoning the vessel.");return false;}
        // A bounded clear volume avoids summoning inside walls, trees or a cave ceiling.
        for(int x=-1;x<=1;x++)for(int y=0;y<4;y++)for(int z=-1;z<=1;z++){
            var check=at.clone().add(x,y,z);if(!Bukkit.isOwnedByCurrentRegion(check)||!check.getBlock().getType().isAir()){
                plugin.send(player,"<yellow>The vessel needs a clear space above solid ground.");return false;
            }
        }
        if(!bossSlots.tryAcquire())return false;
        Wither wither;
        try{wither=at.getWorld().spawn(at,Wither.class,w->{mark(w,player,"boss");w.setVisibleByDefault(false);
            w.customName(Text.mm("<gold>The Hollow King's vessel"));w.setInvulnerableTicks(0);w.setRemoveWhenFarAway(false);w.setCanTravelThroughPortals(false);
            if(w.getBossBar()!=null)w.getBossBar().setVisible(false);
        });}catch(RuntimeException error){bossSlots.release();plugin.send(player,"<yellow>The vessel could not enter this area. Try another clear spot.");return false;}
        if(!wither.isValid()){bossSlots.release();return false;}
        Session session=new Session(player,BOSS_QUEST,wither);bosses.put(id,session);player.showEntity(plugin,wither);
        wither.getScheduler().runAtFixedRate(plugin,t->{if(!tick(session,true))t.cancel();},()->retired(bosses,id,session),1,5);
        plugin.send(player,"<gold>The vessel wakes. <white>Stand your ground.");return true;
    }
    private final class BossMenu implements LockedMenu{
        final Player player;Inventory inventory;boolean used;
        BossMenu(Player player){this.player=player;}
        public Inventory getInventory(){return inventory;}public UUID viewer(){return player.getUniqueId();}
        public void click(int slot,ClickType type){
            if(slot==26){player.closeInventory();return;}
            if(slot!=13||used||!plugin.memories().near(player,"aldis"))return;
            used=true;player.closeInventory();summon(player);
        }
    }
    private void stop(Map<UUID,Session> map,UUID id,Session session){
        retired(map,id,session);
        if(Bukkit.isOwnedByCurrentRegion(session.mob))session.mob.remove();else Sched.entity(session.mob,session.mob::remove);
    }
    private void retired(Map<UUID,Session> map,UUID id,Session session){
        session.active=false;map.remove(id,session);
        if(session.released.compareAndSet(false,true)){
            (map==bosses?bossSlots:helperSlots).release();
            if(map==companions)plugin.nameplates().remove("companion_"+id);
        }
    }
    public void forget(Player player){UUID id=player.getUniqueId();var a=companions.get(id);if(a!=null)stop(companions,id,a);var b=bosses.get(id);if(b!=null)stop(bosses,id,b);retry.remove(id);helpCooldown.remove(id);}
    public void clear(){for(var s:List.copyOf(companions.values()))stop(companions,s.player.getUniqueId(),s);for(var s:List.copyOf(bosses.values()))stop(bosses,s.player.getUniqueId(),s);retry.clear();helpCooldown.clear();}
    public void shutdown(){running=false;clear();}

    private Entity source(Entity entity){return entity instanceof Projectile p&&p.getShooter() instanceof Entity shooter?shooter:entity;}
    private UUID attackOwner(Entity entity){UUID own=owner(entity);return own!=null?own:owner(source(entity));}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void damage(EntityDamageByEntityEvent event){
        UUID attacker=attackOwner(event.getDamager()),victim=owner(event.getEntity());
        if(attacker!=null&&!attacker.equals(event.getEntity().getUniqueId()))event.setCancelled(true);
        if(victim!=null&&(!"boss".equals(event.getEntity().getPersistentDataContainer().get(kindKey,PersistentDataType.STRING))
                ||!victim.equals(source(event.getDamager()).getUniqueId())))event.setCancelled(true);
    }
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true)
    public void combat(EntityDamageByEntityEvent event){
        Entity src=source(event.getDamager());
        if(!(src instanceof Player player)||!(event.getEntity() instanceof Monster target)||marked(target))return;
        Session s=companions.get(player.getUniqueId());if(s==null)return;
        // Help only with monsters named by this active quest, never PvP, pets or passive mobs.
        var quest=plugin.quests().get(s.quest);if(quest==null||quest.objectives().stream().noneMatch(o->o.type()==ObjectiveType.KILL&&o.target().matches(target.getType().name())))return;
        if(!Bukkit.isOwnedByCurrentRegion(player)||!same(player.getLocation(),target.getLocation(),4)||!same(s.helperAt,target.getLocation(),6))return;
        long now=System.nanoTime();Long due=helpCooldown.putIfAbsent(player.getUniqueId(),now+1_000_000_000L);
        if(due!=null){if(now<due)return;helpCooldown.put(player.getUniqueId(),now+1_000_000_000L);}
        Sched.entity(target,()->{
            if(!s.active||companions.get(player.getUniqueId())!=s||!target.isValid()||!Bukkit.isOwnedByCurrentRegion(player)
                    ||!active(player,s.quest)||!same(player.getLocation(),target.getLocation(),4)||!same(s.helperAt,target.getLocation(),6))return;
            target.damage(2,player);
        });
    }
    private final Map<UUID,Long> helpCooldown=new ConcurrentHashMap<>();
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void target(EntityTargetLivingEntityEvent event){UUID id=owner(event.getEntity());if(id!=null&&(event.getTarget()==null||!id.equals(event.getTarget().getUniqueId())))event.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void launch(ProjectileLaunchEvent event){
        if(event.getEntity().getShooter() instanceof Entity shooter){UUID id=owner(shooter);if(id!=null){
            event.getEntity().getPersistentDataContainer().set(ownerKey,PersistentDataType.STRING,id.toString());event.getEntity().setPersistent(false);
            event.getEntity().setVisibleByDefault(false);
            Player player=Bukkit.getPlayer(id);if(player!=null)Sched.entity(player,()->player.showEntity(plugin,event.getEntity()));
            event.getEntity().getScheduler().runDelayed(plugin,t->event.getEntity().remove(),null,200);
        }}
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void explode(EntityExplodeEvent event){if(attackOwner(event.getEntity())!=null){event.blockList().clear();event.setYield(0);}}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void block(EntityChangeBlockEvent event){if(marked(event.getEntity()))event.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void portal(EntityPortalEvent event){if(marked(event.getEntity()))event.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void interact(PlayerInteractEntityEvent event){if(marked(event.getRightClicked()))event.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void interactAt(PlayerInteractAtEntityEvent event){interact(event);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void leash(PlayerLeashEntityEvent event){if(marked(event.getEntity()))event.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void transform(EntityTransformEvent event){if(marked(event.getEntity()))event.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void vehicle(VehicleEnterEvent event){if(marked(event.getEntered()))event.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST)
    public void death(EntityDeathEvent event){
        UUID id=owner(event.getEntity());if(id==null)return;event.getDrops().clear();event.setDroppedExp(0);
        var session=bosses.get(id);
        if(session!=null&&session.mob.getUniqueId().equals(event.getEntity().getUniqueId())&&bosses.remove(id,session)){
            retired(bosses,id,session);Sched.entity(session.player,()->{if(running&&active(session.player,BOSS_QUEST))plugin.questManager().progress(session.player,ObjectiveType.KILL,"WITHER",1);});
        }
    }
    @EventHandler public void load(EntitiesLoadEvent event){for(Entity entity:event.getEntities())if(marked(entity))entity.remove();}
    @EventHandler public void quit(PlayerQuitEvent event){forget(event.getPlayer());plugin.memories().forget(event.getPlayer());helpCooldown.remove(event.getPlayer().getUniqueId());}
    @EventHandler public void died(PlayerDeathEvent event){forget(event.getEntity());}
}
