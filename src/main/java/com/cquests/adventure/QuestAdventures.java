package com.cquests.adventure;

import com.cquests.T;

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
import org.bukkit.entity.Ageable;
import java.util.concurrent.ConcurrentHashMap;

/** Small, player-owned encounters. Entity work stays on its owner scheduler. */
public final class QuestAdventures implements Listener {
    /** One private boss fight from bosses.yml, keyed by the quest it finishes. */
    public record Boss(String quest,String giver,EntityType entity,String name,double health,Material weapon,EntityType minion,int minions,Set<String> events){}
    private volatile Map<String,Boss> bossDefs=Map.of();
    private volatile boolean bossesEnabled=true;
    private volatile java.util.concurrent.Semaphore bossSlots=new java.util.concurrent.Semaphore(6);
    private static final Set<String> ESCORTS=Set.of("story_martha","story_iona");
    private static final class Session {
        final Player player;final String quest;final Mob mob;
        final long born=System.nanoTime();final Location origin;
        volatile Location playerAt;volatile boolean active=true;
        volatile Location helperAt;
        Boss boss;java.util.concurrent.Semaphore slots;final List<Mob> minions=new java.util.concurrent.CopyOnWriteArrayList<>();
        volatile boolean phased,test;long nextEvent;Villager pip;String pipMode;long pipNext;net.kyori.adventure.bossbar.BossBar bar;
        final java.util.concurrent.atomic.AtomicBoolean released=new java.util.concurrent.atomic.AtomicBoolean();
        Session(Player player,String quest,Mob mob){this.player=player;this.quest=quest;this.mob=mob;origin=mob.getLocation();helperAt=origin;playerAt=player.getLocation();}
    }
    private final CQuestsPlugin plugin;
    private final NamespacedKey ownerKey,kindKey;
    private final Map<UUID,Session> companions=new ConcurrentHashMap<>(),bosses=new ConcurrentHashMap<>();
    private final Map<UUID,Long> retry=new ConcurrentHashMap<>();
    private final java.util.concurrent.Semaphore helperSlots=new java.util.concurrent.Semaphore(32);
    private volatile boolean running=true;
    public QuestAdventures(CQuestsPlugin plugin){this.plugin=plugin;ownerKey=new NamespacedKey(plugin,"adventure_owner");kindKey=new NamespacedKey(plugin,"adventure_kind");reloadBosses();}

    /** Reads bosses.yml. Running fights keep their settings until they end. */
    public void reloadBosses(){
        var file=new java.io.File(plugin.getDataFolder(),"bosses.yml");
        var yaml=org.bukkit.configuration.file.YamlConfiguration.loadConfiguration(file);
        if(!file.exists())try(var in=plugin.getResource("bosses.yml")){if(in!=null)yaml=org.bukkit.configuration.file.YamlConfiguration.loadConfiguration(new java.io.InputStreamReader(in,java.nio.charset.StandardCharsets.UTF_8));}catch(java.io.IOException ignored){}
        var next=new HashMap<String,Boss>();var root=yaml.getConfigurationSection("bosses");
        if(root!=null)for(String quest:root.getKeys(false)){
            var b=root.getConfigurationSection(quest);if(b==null)continue;
            EntityType type=entity(b.getString("entity","")),minion=entity(b.getString("minions","NONE"));
            if(type==null||!Mob.class.isAssignableFrom(type.getEntityClass()==null?Object.class:type.getEntityClass())){plugin.getLogger().warning("bosses.yml: "+quest+" needs a mob type in entity");continue;}
            Material weapon=b.getString("weapon","").isBlank()?null:Material.matchMaterial(b.getString("weapon",""));
            var events=new HashSet<String>();for(String e:b.getStringList("events"))events.add(e.toLowerCase(Locale.ROOT));
            next.put(quest.toLowerCase(Locale.ROOT),new Boss(quest.toLowerCase(Locale.ROOT),b.getString("giver","").toLowerCase(Locale.ROOT),type,
                    b.getString("name","<red>"+quest),Math.max(0,Math.min(1024,b.getDouble("health",0))),weapon,
                    minion!=null&&minion.getEntityClass()!=null&&Mob.class.isAssignableFrom(minion.getEntityClass())?minion:null,
                    Math.max(0,Math.min(6,b.getInt("minion-count",0))),Set.copyOf(events)));
        }
        bossDefs=Map.copyOf(next);bossesEnabled=yaml.getBoolean("enabled",true);
        int max=Math.max(1,Math.min(32,yaml.getInt("max-active",6)));
        if(bosses.isEmpty())bossSlots=new java.util.concurrent.Semaphore(max);
    }
    public boolean bossesEnabled(){return bossesEnabled;}
    private static EntityType entity(String name){
        if(name==null||name.isBlank()||name.equalsIgnoreCase("NONE"))return null;
        try{return EntityType.valueOf(name.trim().toUpperCase(Locale.ROOT));}catch(IllegalArgumentException e){return null;}
    }
    /** True for quests finished by a private boss fight; ordinary kills don't count for them. */
    public boolean isBossQuest(String quest){return bossDefs.containsKey(quest);}
    private Boss activeBoss(Player player,String giver){
        for(Boss b:bossDefs.values())if((giver==null||b.giver().equals(giver))&&plugin.quests().get(b.quest())!=null&&active(player,b.quest()))return b;
        return null;
    }
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
        if(boss!=null){if(!player.isOnline()||player.isDead()||(!boss.test&&(!playable(player)||!active(player,boss.quest)))||!same(boss.origin,player.getLocation(),48))stop(bosses,id,boss);else boss.playerAt=player.getLocation();}
        if(helper!=null){if(!player.isOnline()||player.isDead()||(helper.test&&System.nanoTime()-helper.born>60_000_000_000L)||(!helper.test&&(!playable(player)||!active(player,helper.quest)))||!helper.origin.getWorld().equals(player.getWorld()))stop(companions,id,helper);else helper.playerAt=player.getLocation();return;}
        if(!plugin.getConfig().getBoolean("adventures.companions",true)||!playable(player)||companions.size()>=32||System.nanoTime()<retry.getOrDefault(id,0L))return;
        for(String quest:ESCORTS)if(active(player,quest)){
            retry.put(id,System.nanoTime()+10_000_000_000L);
            spawnCompanion(player,quest,false);
            return;
        }
    }
    /** Pip the escort companion: follows the player, invisible to everyone else. */
    private boolean spawnCompanion(Player player,String quest,boolean test){
        UUID id=player.getUniqueId();
        Location at=ground(player.getLocation(),2);if(at==null)return false;
        if(!helperSlots.tryAcquire())return false;
        Villager villager;
        try{villager=at.getWorld().spawn(at,Villager.class,v->{
            mark(v,player,"companion");v.customName(null);
            v.setCustomNameVisible(false);v.setInvulnerable(true);v.setCollidable(false);v.setSilent(true);v.setVisibleByDefault(false);
            v.setRemoveWhenFarAway(false);v.setCanPickupItems(false);v.setProfession(Villager.Profession.WEAPONSMITH);v.setAdult();v.setBreed(false);
        });}catch(RuntimeException error){helperSlots.release();plugin.getLogger().warning("Companion spawn declined: "+error.getMessage());return false;}
        if(!villager.isValid()){helperSlots.release();return false;}
        var session=new Session(player,quest,villager);session.test=test;companions.put(id,session);player.showEntity(plugin,villager);
        String label="companion_"+id;
        plugin.nameplates().spawn(new NpcDef(label,"<gold>Pip</gold>","Your companion","WEAPONSMITH","PLAINS",
                plugin.progression().level(plugin.questManager().data(player)),1,true,false,false,"",List.of(),List.of()),villager,at);
        plugin.nameplates().show(player,label,true);
        plugin.send(player,T.t("quest-adventures.jogs-up-beside-you", "<pip> <gray>jogs up beside you. <white><player>", "pip", plugin.characters().label("pip","<gold>Pip"), "player", plugin.characters().text("pip","arrival",plugin.memories().companionLine(plugin.questManager().data(player)))));
        villager.getScheduler().runAtFixedRate(plugin,t->{if(!tick(session,false)){t.cancel();return;}},()->retired(companions,id,session),5,5);
        return true;
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
            if(!Bukkit.isOwnedByCurrentRegion(session.player)){stop(sessions,id,session);return false;}
            bossTick(session);
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
        Boss b=activeBoss(player,npc.id());if(b==null)return false;
        Inventory inv=Bukkit.createInventory(new BossMenu(player,b),27,Text.mm("<dark_gray>"+Text.plain(Text.mm(b.name()))));
        var menu=(BossMenu)inv.getHolder();menu.inventory=inv;
        for(int i=0;i<27;i++)inv.setItem(i,QuestMenu.item(Material.BLACK_STAINED_GLASS_PANE," ",List.of()));
        inv.setItem(13,QuestMenu.item(Material.WITHER_SKELETON_SKULL,"<gold><bold>Face "+b.name(),List.of(
                "<white>It will hunt you alone.","<gray>Nobody else can fight it or be hurt by it.","<gray>It breaks no blocks and drops nothing.",
                "<gray>Leave the area, fall, or log out and it withdraws.","<yellow>Click when you are ready.")));
        int left=pipLeft(player);
        if(left>0){
            inv.setItem(15,QuestMenu.item(Material.BOW,"<gold>Face it with Pip <gray>(bow)",List.of("<white>Pip shoots it from a distance.","<gray>Pip can help in "+left+" more boss fight"+(left==1?"":"s")+".")));
            inv.setItem(16,QuestMenu.item(Material.IRON_SWORD,"<gold>Face it with Pip <gray>(sword)",List.of("<white>Pip fights it up close.","<gray>Pip can help in "+left+" more boss fight"+(left==1?"":"s")+".")));
        }
        inv.setItem(26,QuestMenu.item(Material.BARRIER,"<gray>Not yet",List.of()));player.openInventory(inv);return true;
    }
    /** /quests encounter: calls the boss of whichever boss quest the player has open. */
    public boolean summon(Player player){Boss b=activeBoss(player,null);return b!=null&&summon(player,b);}
    public boolean summon(Player player,Boss b){return summon(player,b,false,null);}
    /** Boss quest ids for /cq test boss. */
    public java.util.Collection<String> bossIds(){return new java.util.TreeSet<>(bossDefs.keySet());}
    /**
     * /cq test boss: the real fight for an admin, in any game mode, without the quest or the villager.
     * Nothing counts and nothing drops. Creative players can watch it without being hurt.
     */
    public boolean testBoss(Player player,String quest){
        Boss b=bossDefs.get(quest.toLowerCase(Locale.ROOT));
        if(b==null){plugin.send(player,T.t("quest-adventures.no-boss-for-bosses", "<red>No boss for <quest>. Bosses: <white><bossids>", "quest", Text.escape(quest), "bossids", String.join(", ",bossIds())));return false;}
        var old=bosses.get(player.getUniqueId());if(old!=null)stop(bosses,player.getUniqueId(),old);
        return summon(player,b,true,null);
    }
    /** /cq test pip: a test boss with Pip fighting at your side. */
    public boolean testPip(Player player,String mode){
        String quest=bossDefs.containsKey("story_ironjaw_hunter")?"story_ironjaw_hunter":bossIds().stream().findFirst().orElse("");
        Boss b=bossDefs.get(quest);if(b==null)return false;
        var old=bosses.get(player.getUniqueId());if(old!=null)stop(bosses,player.getUniqueId(),old);
        return summon(player,b,true,"sword".equalsIgnoreCase(mode)?"sword":"bow");
    }
    /** Boss fights Pip can still help with for this player (adventures.pip-boss-help, 3 by default). */
    public int pipLeft(Player player){
        int max=Math.max(0,plugin.getConfig().getInt("adventures.pip-boss-help",3));
        return Math.max(0,max-plugin.questManager().data(player).pipHelped());
    }
    /** Jumps the test boss to half health so the phase, minions and events play now. */
    /** /cq test companion: Pip the escort follows you for a minute or until /cq test bossstop, nothing counts. */
    public boolean testCompanion(Player player){
        if(!running)return false;
        var old=companions.get(player.getUniqueId());if(old!=null)stop(companions,player.getUniqueId(),old);
        return spawnCompanion(player,ESCORTS.iterator().next(),true);
    }
    public boolean testPhase(Player player){
        var session=bosses.get(player.getUniqueId());if(session==null||!session.test)return false;
        Sched.entity(session.mob,()->{if(session.mob.isValid())session.mob.setHealth(Math.max(1,maxHealthOf(session.mob)/2-1));});return true;
    }
    public boolean testStop(Player player){var helper=companions.get(player.getUniqueId());if(helper!=null&&helper.test)stop(companions,player.getUniqueId(),helper);var session=bosses.get(player.getUniqueId());if(session==null)return helper!=null&&helper.test;stop(bosses,player.getUniqueId(),session);return true;}
    /** Plays one boss event on the player alone. */
    public boolean testEvent(Player player,String event){
        String e=event.toLowerCase(Locale.ROOT);if(!EVENTS.contains(e))return false;
        Location at=player.getLocation();
        if(e.equals("lightning"))for(int i=0;i<3;i++){Location strike=at.clone().add(java.util.concurrent.ThreadLocalRandom.current().nextInt(-5,6),0,java.util.concurrent.ThreadLocalRandom.current().nextInt(-5,6));if(Bukkit.isOwnedByCurrentRegion(strike))strike.getWorld().strikeLightningEffect(strike);}
        else effect(player,e,at.clone().add(at.getDirection().multiply(3)));
        return true;
    }
    public static final List<String> EVENTS=List.of("lightning","darkness","slowness","levitate","roar");
    private boolean summon(Player player,Boss b,boolean test,String pipMode){
        UUID id=player.getUniqueId();
        if(player.getWorld().getDifficulty()==Difficulty.PEACEFUL){plugin.send(player,T.t("quest-adventures.bosses-cannot-wake-in-a", "<yellow>Bosses cannot wake in a Peaceful world."));return false;}
        boolean allowed=b.quest().equals("story_aldis")?plugin.getConfig().getBoolean("adventures.wither",true):true;
        if(!running||!bossesEnabled||!allowed||!plugin.getConfig().getBoolean("adventures.enabled",true)
                ||(!test&&(!playable(player)||!active(player,b.quest())))||bosses.containsKey(id))return false;
        if(!test&&!plugin.memories().near(player,b.giver())){plugin.send(player,T.t("quest-adventures.stand-near-to-call-it", "<yellow>Stand near <giver> to call it.", "giver", Text.escape(plugin.npcs().name(b.giver()))));return false;}
        Location at=ground(player.getLocation(),6);
        if(at==null){plugin.send(player,T.t("quest-adventures.find-clear-solid-ground-with", "<yellow>Find clear, solid ground with space beside you first."));return false;}
        // A bounded clear volume avoids summoning inside walls, trees or a cave ceiling.
        for(int x=-1;x<=1;x++)for(int y=0;y<4;y++)for(int z=-1;z<=1;z++){
            var check=at.clone().add(x,y,z);if(!Bukkit.isOwnedByCurrentRegion(check)||!check.getBlock().getType().isAir()){
                plugin.send(player,T.t("quest-adventures.it-needs-a-clear-space", "<yellow>It needs a clear space above solid ground."));return false;
            }
        }
        var slots=bossSlots;
        if(!slots.tryAcquire()){plugin.send(player,T.t("quest-adventures.too-many-boss-fights-are", "<yellow>Too many boss fights are running on the server. Try again in a minute."));return false;}
        Mob mob;
        try{mob=(Mob)at.getWorld().spawn(at,b.entity().getEntityClass(),e->{
            mark(e,player,"boss");e.setVisibleByDefault(false);
            if(e instanceof Mob m){m.customName(Text.mm(b.name()));m.setCustomNameVisible(true);m.setRemoveWhenFarAway(false);m.setCanPickupItems(false);
                if(b.health()>0)maxHealth(m,b.health());
                if(b.weapon()!=null&&m.getEquipment()!=null){m.getEquipment().setItemInMainHand(new org.bukkit.inventory.ItemStack(b.weapon()));m.getEquipment().setItemInMainHandDropChance(0f);}
                if(m instanceof Ageable a)a.setAdult();}
            if(e instanceof Wither w){w.setInvulnerableTicks(0);if(w.getBossBar()!=null)w.getBossBar().setVisible(false);}
        });}catch(RuntimeException error){slots.release();plugin.send(player,T.t("quest-adventures.it-could-not-enter-this", "<yellow>It could not enter this area. Try another clear spot."));return false;}
        if(!mob.isValid()){slots.release();return false;}
        Session session=new Session(player,b.quest(),mob);session.boss=b;session.test=test;
        if(pipMode!=null&&(test||pipLeft(player)>0)){
            Location spot=ground(player.getLocation(),-2);
            if(spot!=null){
                try{session.pip=spot.getWorld().spawn(spot,Villager.class,v->{
                    mark(v,player,"pip");v.setVisibleByDefault(false);v.setInvulnerable(true);v.setCollidable(false);v.setSilent(true);
                    v.setRemoveWhenFarAway(false);v.setCanPickupItems(false);v.setProfession(Villager.Profession.WEAPONSMITH);v.setAdult();v.setBreed(false);
                    v.customName(Text.mm(T.t("quest-adventures.pip", "<gold>Pip")));v.setCustomNameVisible(true);
                    if(v.getEquipment()!=null)v.getEquipment().setItemInMainHand(new org.bukkit.inventory.ItemStack("sword".equals(pipMode)?Material.IRON_SWORD:Material.BOW));
                });
                session.pipMode=pipMode;player.showEntity(plugin,session.pip);
                if(!test)plugin.questManager().data(player).addPipHelped();
                plugin.send(player,T.t("quest-adventures.pip-runs-in-with", "<gold>Pip <white>runs in with <bow>! <gray><with>", "bow", ("sword".equals(pipMode)?"a sword":"a bow"), "with", (test?"(test)":pipLeft(player)+" more fights Pip can help with.")));
                }catch(RuntimeException ignored){session.pip=null;}
            }
        }session.slots=slots;session.nextEvent=System.nanoTime()+20_000_000_000L;
        session.bar=net.kyori.adventure.bossbar.BossBar.bossBar(Text.mm(b.name()),1f,net.kyori.adventure.bossbar.BossBar.Color.RED,net.kyori.adventure.bossbar.BossBar.Overlay.NOTCHED_10);
        bosses.put(id,session);player.showEntity(plugin,mob);player.showBossBar(session.bar);
        mob.getScheduler().runAtFixedRate(plugin,t->{if(!tick(session,true))t.cancel();},()->retired(bosses,id,session),1,5);
        player.showTitle(net.kyori.adventure.title.Title.title(Text.mm(b.name()),Text.mm(T.t("quest-adventures.stand-your-ground", "<gray>Stand your ground."))));
        if(test)plugin.send(player,T.t("quest-adventures.test-fight-nothing-counts-and", "<gray>Test fight: nothing counts and nothing drops. <yellow>/cq test bossphase</yellow> jumps to half health, <yellow>/cq test bossstop</yellow> ends it."));
        plugin.send(player,T.t("quest-adventures.wakes-stand-your-ground", "<name> <gold>wakes. <white>Stand your ground.", "name", b.name()));return true;
    }
    private static void maxHealth(LivingEntity e,double health){
        var registry=org.bukkit.Registry.ATTRIBUTE;
        var attribute=registry.get(NamespacedKey.minecraft("max_health"));
        if(attribute==null)attribute=registry.get(NamespacedKey.minecraft("generic.max_health"));
        var instance=attribute==null?null:e.getAttribute(attribute);
        if(instance!=null){instance.setBaseValue(health);e.setHealth(health);}
    }
    /** Runs on the boss's region with the player in the same region (checked by tick). */
    private void bossTick(Session session){
        Mob mob=session.mob;Player player=session.player;Boss b=session.boss;
        if(mob instanceof Wither w)for(var head:Wither.Head.values())w.setTarget(head,player);
        else{mob.setTarget(player);if(mob instanceof Warden warden)warden.setAnger(player,150);}
        pipTick(session);
        for(Mob minion:session.minions){
            if(!minion.isValid()){session.minions.remove(minion);continue;}
            if(Bukkit.isOwnedByCurrentRegion(minion))minion.setTarget(player);
        }
        double max=maxHealthOf(mob);
        if(session.bar!=null)session.bar.progress((float)Math.max(0,Math.min(1,mob.getHealth()/Math.max(1,max))));
        if(b==null)return;
        if(!session.phased&&mob.getHealth()<=max/2){
            session.phased=true;
            player.showTitle(net.kyori.adventure.title.Title.title(Text.mm(b.name()),Text.mm(T.t("quest-adventures.is-furious", "<red>is furious!"))));
            if(session.bar!=null)session.bar.color(net.kyori.adventure.bossbar.BossBar.Color.PURPLE);
            events(session);
            if(b.minion()!=null)for(int i=0;i<b.minions();i++){
                Location at=mob.getLocation().clone().add(java.util.concurrent.ThreadLocalRandom.current().nextInt(-3,4),0,java.util.concurrent.ThreadLocalRandom.current().nextInt(-3,4));
                if(!Bukkit.isOwnedByCurrentRegion(at))continue;
                try{var minion=at.getWorld().spawn(at,b.minion().getEntityClass(),e->{mark(e,player,"minion");e.setVisibleByDefault(false);
                    if(e instanceof Mob m){m.setRemoveWhenFarAway(false);m.setCanPickupItems(false);}});
                    if(minion instanceof Mob m&&m.isValid()){session.minions.add(m);player.showEntity(plugin,m);m.setTarget(player);}else minion.remove();
                }catch(RuntimeException ignored){}
            }
        }else if(session.phased&&System.nanoTime()>=session.nextEvent){events(session);}
    }
    /** Pip follows the fight and hits the boss: an arrow every 1.5 s from range, or a sword swing up close. */
    private void pipTick(Session session){
        Villager pip=session.pip;if(pip==null)return;
        if(!pip.isValid()||!Bukkit.isOwnedByCurrentRegion(pip)){session.pip=null;return;}
        Mob boss=session.mob;Location from=pip.getLocation(),to=boss.getLocation();
        if(!from.getWorld().equals(to.getWorld())){return;}
        double distance=from.distance(to);boolean sword="sword".equals(session.pipMode);
        double keep=sword?1.8:7;
        if(distance>keep+1)pip.getPathfinder().moveTo(sword?to:session.playerAt,1.2);else pip.getPathfinder().stopPathfinding();
        pip.lookAt(to.clone().add(0,1,0));
        long now=System.nanoTime();if(now<session.pipNext)return;
        if(sword&&distance<=3.2){session.pipNext=now+1_200_000_000L;pip.swingMainHand();boss.damage(5);
            from.getWorld().playSound(from,Sound.ENTITY_PLAYER_ATTACK_SWEEP,0.8f,1.2f);}
        else if(!sword&&distance<=24){session.pipNext=now+1_500_000_000L;
            var start=from.clone().add(0,1.4,0);var step=to.clone().add(0,1,0).toVector().subtract(start.toVector());
            int points=(int)Math.min(24,Math.max(2,distance*2));step.multiply(1.0/points);
            for(int i=0;i<points;i++){var p=start.clone().add(step.clone().multiply(i));session.player.spawnParticle(Particle.CRIT,p,1,0,0,0,0);}
            session.player.playSound(from,Sound.ENTITY_ARROW_SHOOT,0.8f,1f);boss.damage(4);
        }
    }
    private static double maxHealthOf(LivingEntity e){
        var attribute=org.bukkit.Registry.ATTRIBUTE.get(NamespacedKey.minecraft("max_health"));
        if(attribute==null)attribute=org.bukkit.Registry.ATTRIBUTE.get(NamespacedKey.minecraft("generic.max_health"));
        var instance=attribute==null?null:e.getAttribute(attribute);return instance==null?Math.max(1,e.getHealth()):instance.getValue();
    }
    /** The boss's special moves. Only the fighting player is affected; lightning is visual only. */
    private void events(Session session){
        session.nextEvent=System.nanoTime()+20_000_000_000L;
        Player player=session.player;Set<String> events=session.boss.events();Location at=player.getLocation();
        if(events.contains("lightning"))for(int i=0;i<3;i++){
            Location strike=at.clone().add(java.util.concurrent.ThreadLocalRandom.current().nextInt(-5,6),0,java.util.concurrent.ThreadLocalRandom.current().nextInt(-5,6));
            if(Bukkit.isOwnedByCurrentRegion(strike))strike.getWorld().strikeLightningEffect(strike);
        }
        for(String e:List.of("darkness","slowness","levitate","roar"))if(events.contains(e))effect(player,e,session.mob.getLocation());
    }
    private static void effect(Player player,String event,Location from){
        Location at=player.getLocation();
        switch(event){
            case "darkness" -> player.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.DARKNESS,100,0,false,false,true));
            case "slowness" -> player.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SLOWNESS,80,1,false,false,true));
            case "levitate" -> player.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.LEVITATION,30,0,false,false,true));
            case "roar" -> {
                player.playSound(at,Sound.ENTITY_RAVAGER_ROAR,1f,0.7f);
                var push=at.toVector().subtract(from.toVector()).setY(0);
                if(push.lengthSquared()>0.01)player.setVelocity(push.normalize().multiply(1.2).setY(0.45));
            }
            default -> {}
        }
    }
    private final class BossMenu implements LockedMenu{
        final Player player;final Boss boss;Inventory inventory;boolean used;
        BossMenu(Player player,Boss boss){this.player=player;this.boss=boss;}
        public Inventory getInventory(){return inventory;}public UUID viewer(){return player.getUniqueId();}
        public void click(int slot,ClickType type){
            if(slot==26){player.closeInventory();return;}
            if((slot!=13&&slot!=15&&slot!=16)||used||!plugin.memories().near(player,boss.giver()))return;
            if(slot!=13&&pipLeft(player)<=0)return;
            used=true;player.closeInventory();summon(player,boss,false,slot==15?"bow":slot==16?"sword":null);
        }
    }
    private void stop(Map<UUID,Session> map,UUID id,Session session){
        retired(map,id,session);
        if(Bukkit.isOwnedByCurrentRegion(session.mob))session.mob.remove();else Sched.entity(session.mob,session.mob::remove);
    }
    private void retired(Map<UUID,Session> map,UUID id,Session session){
        session.active=false;map.remove(id,session);
        if(session.released.compareAndSet(false,true)){
            if(map==bosses){if(session.slots!=null)session.slots.release();}else helperSlots.release();
            if(map==companions)plugin.nameplates().remove("companion_"+id);
            if(session.bar!=null){var bar=session.bar;var p=session.player;if(p.isOnline())Sched.entity(p,()->p.hideBossBar(bar));}
            for(Mob minion:session.minions){if(Bukkit.isOwnedByCurrentRegion(minion))minion.remove();else Sched.entity(minion,minion::remove);}
            var pip=session.pip;session.pip=null;
            if(pip!=null){if(Bukkit.isOwnedByCurrentRegion(pip))pip.remove();else Sched.entity(pip,pip::remove);}
            session.minions.clear();
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
        String kind=event.getEntity().getPersistentDataContainer().get(kindKey,PersistentDataType.STRING);
        if(victim!=null&&(!("boss".equals(kind)||"minion".equals(kind))
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
    /** Boss fireballs and lightning never set the world on fire. */
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void ignite(org.bukkit.event.block.BlockIgniteEvent event){if(event.getIgnitingEntity()!=null&&attackOwner(event.getIgnitingEntity())!=null)event.setCancelled(true);}
    /** Undead bosses and minions don't burn away in daylight. */
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void sunburn(EntityCombustEvent event){if(!(event instanceof EntityCombustByEntityEvent)&&!(event instanceof EntityCombustByBlockEvent)&&marked(event.getEntity()))event.setCancelled(true);}
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
            retired(bosses,id,session);String type=event.getEntity().getType().name();Boss b=session.boss;
            if(session.test){Sched.entity(session.player,()->plugin.send(session.player,T.t("quest-adventures.test-boss-defeated-nothing-was", "<green>Test boss defeated. <gray>Nothing was counted.")));return;}
            Sched.entity(session.player,()->{if(running&&active(session.player,session.quest)){
                plugin.questManager().progress(session.player,ObjectiveType.KILL,type,1,true);
                if(b!=null&&plugin.discord()!=null)plugin.discord().bossDefeated(session.player,Text.plain(Text.mm(b.name())));
            }});
        }
    }
    @EventHandler public void load(EntitiesLoadEvent event){for(Entity entity:event.getEntities())if(marked(entity))entity.remove();}
    @EventHandler public void quit(PlayerQuitEvent event){forget(event.getPlayer());plugin.memories().forget(event.getPlayer());helpCooldown.remove(event.getPlayer().getUniqueId());}
    @EventHandler public void died(PlayerDeathEvent event){forget(event.getEntity());}
}
