package com.cquests.dialogue;

import com.cquests.CQuestsPlugin;
import com.cquests.model.NpcDef;
import com.cquests.util.Sched;
import com.cquests.util.Text;
import io.papermc.paper.event.player.AsyncChatEvent;
import io.papermc.paper.threadedregions.scheduler.ScheduledTask;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.NamedTextColor;
import org.bukkit.Location;
import org.bukkit.Sound;
import org.bukkit.entity.Display;
import org.bukkit.entity.Player;
import org.bukkit.entity.TextDisplay;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/** One private hologram and one repeating task per active conversation, never per idle NPC. */
public final class SpeechController implements Listener {
    private static final class Session {
        final String npc; final Location anchor; final List<String> sentences; final Runnable open;
        final SpeechChatBuffer chat=new SpeechChatBuffer();final UUID token=UUID.randomUUID();final SpeechTiming timing;
        final SpeechPlayback playback;
        volatile TextDisplay display; ScheduledTask task; int letters,characterWait,rows=1; volatile boolean ready; boolean idle; long readyUntil;
        Session(String npc,Location anchor,List<String> sentences,Runnable open,SpeechTiming timing) {
            this.timing=timing;this.npc=npc;this.anchor=anchor;this.sentences=sentences;this.open=open;
            this.playback=new SpeechPlayback(sentences,timing);
        }
    }
    private final CQuestsPlugin plugin;
    private final Map<UUID,Session> sessions=new ConcurrentHashMap<>();
    public SpeechController(CQuestsPlugin plugin) {this.plugin=plugin;}
    public boolean busy(Player p) {Session s=sessions.get(p.getUniqueId());return s!=null&&!s.ready;}
    /** Clicking during speech finishes that sentence; clicking after speech opens the choices. */
    public boolean click(Player player,NpcDef npc) {
        Session s=sessions.get(player.getUniqueId());
        if(s==null)return false;
        if(!s.npc.equals(npc.id())) {stop(player);return false;}
        if(s.playback.click()) {stop(player);s.open.run();}
        return true;
    }
    public void start(Player player,NpcDef npc,List<String> rich,Runnable open) {
        var point=plugin.spawns().points().get(npc.id());
        Location at=point==null?player.getLocation():point.location();
        startAt(player,npc,rich,open,at);
    }
    public void startAt(Player player,NpcDef npc,List<String> rich,Runnable open,Location at) {
        stop(player);
        if(at==null)return;
        List<String> sentences=new ArrayList<>();
        for(String line:rich)for(String sentence:SpeechTiming.sentences(Text.plain(Text.mm(line))))
            if(!sentence.isBlank())sentences.add(sentence);
        if(sentences.isEmpty())sentences.add("What do you need, "+player.getName()+"?");
        Session s=new Session(npc.id(),at.clone(),List.copyOf(sentences),open,new SpeechTiming(plugin.getConfig().getInt("dialogue.character-ticks",2),plugin.getConfig().getInt("dialogue.reading-pause-ticks",80)));
        sessions.put(player.getUniqueId(),s);
        plugin.nameplates().begin(npc.id(),s.token);
        Sched.at(at,()->{
            if(sessions.get(player.getUniqueId())!=s)return;
            TextDisplay display=at.getWorld().spawn(at.clone().add(0,2.15,0),TextDisplay.class,d->{
                d.setPersistent(false);d.setVisibleByDefault(false);d.setBillboard(Display.Billboard.CENTER);
                d.setLineWidth(240);d.setShadowed(true);d.setSeeThrough(false);d.text(Component.empty());
            });
            s.display=display;
            var scheduled=player.getScheduler().run(plugin,ignored->{
                if(sessions.get(player.getUniqueId())!=s){Sched.entity(display,display::remove);return;}
                player.showEntity(plugin,display);
                schedule(player,npc,s,1);
            },()->{sessions.remove(player.getUniqueId(),s);retire(s);});
            if(scheduled==null){sessions.remove(player.getUniqueId(),s);retire(s);}
        });
    }
    private void schedule(Player player,NpcDef npc,Session s,long period){
        s.task=player.getScheduler().runAtFixedRate(plugin,t->tick(player,npc,s),()->{sessions.remove(player.getUniqueId(),s);retire(s);},period,period);
        if(s.task==null){sessions.remove(player.getUniqueId(),s);retire(s);}
    }
    private void tick(Player player,NpcDef npc,Session s) {
        if(sessions.get(player.getUniqueId())!=s)return;
        if(!player.getWorld().equals(s.anchor.getWorld())||player.getLocation().distanceSquared(s.anchor)>100){stop(player);return;}
        if(s.ready){
            if(System.currentTimeMillis()>s.readyUntil){stop(player);return;}
            String prompt="Click to continue";
            if(s.letters>=prompt.length()){
                if(!s.idle){s.idle=true;s.task.cancel();schedule(player,npc,s,10);}
                return;
            }
            if(s.characterWait-->0)return;
            s.characterWait=s.timing.characterTicks()-1;s.letters++;
            String visible=prompt.substring(0,s.letters);
            Sched.entity(s.display,()->s.display.text(Component.text(visible,NamedTextColor.YELLOW)));
            if(!Character.isWhitespace(visible.charAt(visible.length()-1)))player.playSound(player.getLocation(),Sound.UI_BUTTON_CLICK,.12f,1.8f);
            return;
        }
        SpeechPlayback.Frame frame=s.playback.tick();
        if(frame==null)return;
        if(frame.ready()){
            if(s.rows!=1){s.rows=1;plugin.nameplates().lines(s.npc,s.token,1);}
            s.ready=true;s.letters=0;s.characterWait=0;s.readyUntil=System.currentTimeMillis()+120_000;flush(player,s);
            Sched.entity(s.display,()->s.display.text(Component.empty()));return;
        }
        String visible=frame.visible();
        int rows=Math.max(1,(visible.codePointCount(0,visible.length())+35)/36);
        if(rows!=s.rows){s.rows=rows;plugin.nameplates().lines(s.npc,s.token,rows);}
        Sched.entity(s.display,()->s.display.text(Component.text(visible,NamedTextColor.WHITE)));
        if(!visible.isEmpty()&&!Character.isWhitespace(visible.charAt(visible.length()-1)))
            player.playSound(player.getLocation(),Sound.UI_BUTTON_CLICK,.12f,1.8f);
        if(frame.completed()!=null)
            player.sendMessage(Text.mm(plugin.characters().speechPrefix(npc)+"<white>"+Text.escape(frame.completed())));
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void chat(AsyncChatEvent event) {
        for(var entry:sessions.entrySet()) {
            Session s=entry.getValue();if(s.ready)continue;
            var viewer=org.bukkit.Bukkit.getPlayer(entry.getKey());
            if(viewer!=null&&event.viewers().contains(viewer)) {
                Component message=event.renderer().render(event.getPlayer(),event.getPlayer().displayName(),event.message(),viewer);
                s.chat.defer(message,()->event.viewers().remove(viewer));
            }
        }
    }
    private void flush(Player player,Session s){for(Component message:s.chat.resume())player.sendMessage(message);}
    private void retire(Session s){plugin.nameplates().end(s.npc,s.token);if(s.task!=null)s.task.cancel();if(s.display!=null&&plugin.isEnabled())Sched.entity(s.display,s.display::remove);}
    public void stop(Player player){Session s=sessions.remove(player.getUniqueId());if(s!=null){retire(s);flush(player,s);}}
    public void stopAll(){for(UUID id:List.copyOf(sessions.keySet())){
        Session s=sessions.remove(id);if(s==null)continue;retire(s);
        Player p=org.bukkit.Bukkit.getPlayer(id);if(p!=null&&plugin.isEnabled())Sched.entity(p,()->flush(p,s));
    }}
}
