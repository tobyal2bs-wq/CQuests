package com.cquests.progression;

import com.cquests.CQuestsPlugin;
import com.cquests.data.ActiveQuest;
import com.cquests.data.PlayerData;
import com.cquests.model.Quest;
import com.cquests.model.QuestCategory;
import com.cquests.util.Text;
import me.clip.placeholderapi.expansion.PlaceholderExpansion;
import org.bukkit.OfflinePlayer;
import org.jetbrains.annotations.NotNull;

import java.time.LocalDate;
import java.util.Locale;

/**
 * Every CQuests number and name for PlaceholderAPI as {@code %cquests_<key>%}.
 * Any number also comes as {@code <key>_formatted} (1,234,567) and {@code <key>_short} (1.2M).
 * Cached reads only: a placeholder never loads a player file, never touches the world and is safe
 * from any thread (scoreboards, tab lists and chat plugins call it off the main thread on Folia).
 */
public final class SkillPlaceholders extends PlaceholderExpansion {
    private final CQuestsPlugin plugin;
    public SkillPlaceholders(CQuestsPlugin plugin){this.plugin=plugin;}
    public @NotNull String getIdentifier(){return "cquests";}
    public @NotNull String getAuthor(){return "CQuests";}
    public @NotNull String getVersion(){return plugin.getPluginMeta().getVersion();}
    public boolean persist(){return true;}

    public String onRequest(OfflinePlayer player,@NotNull String params){
        String key=params.toLowerCase(Locale.ROOT);
        // Server-wide values work without a player.
        switch(key){
            case "chapters" -> {return Integer.toString(chapterCount());}
            case "story_total" -> {return Integer.toString(plugin.quests().story().size());}
            case "bosses_enabled" -> {return yesNo(plugin.adventures()!=null&&plugin.adventures().bossesEnabled());}
            default -> {}
        }
        if(player==null)return "";
        PlayerData data=plugin.store().cached(player.getUniqueId());
        if(key.endsWith("_formatted")||key.endsWith("_short")){
            boolean shortForm=key.endsWith("_short");
            Long n=number(data,key.substring(0,key.lastIndexOf('_')));
            if(n==null)return null;
            return shortForm?Text.compact(n):String.format(Locale.ROOT,"%,d",n);
        }
        Long n=number(data,key);
        if(n!=null)return Long.toString(n);
        return text(data,key);
    }

    /** Numeric placeholders. 0 when the player's data is not in memory. */
    Long number(PlayerData data,String key){
        boolean known=switch(key){
            case "level","xp","xp_required","xp_next_level","xp_progress","sunflowers","wheat","hoe_tier",
                 "quests_completed","story_done","story_total","story_percent","chapter","chapters","side_done",
                 "dailies_done","daily_streak","active","active_story","active_side","active_daily",
                 "npcs_met","active_progress_percent" -> true;
            default -> false;
        };
        if(!known)return null;
        if(key.equals("chapters"))return (long)chapterCount();
        if(key.equals("story_total"))return (long)plugin.quests().story().size();
        if(data==null)return 0L;
        var curve=plugin.progression().curve();
        return switch(key){
            case "level" -> (long)plugin.progression().level(data);
            case "xp" -> data.skillXp();
            case "xp_required","xp_next_level" -> curve.remaining(data.skillXp());
            case "xp_progress" -> Math.round(curve.progress(data.skillXp())*100);
            case "sunflowers" -> data.sunflowers();
            case "wheat" -> data.wheatHarvested();
            case "hoe_tier" -> (long)data.hoeTier();
            case "quests_completed" -> (long)data.completedCount();
            case "story_done" -> (long)storyDone(data);
            case "story_percent" -> {int total=plugin.quests().story().size();yield total==0?0L:Math.round(storyDone(data)*100.0/total);}
            case "chapter" -> (long)chapter(data);
            case "side_done" -> data.totalSideDone();
            case "dailies_done" -> (long)data.dailiesDone();
            case "daily_streak" -> (long)data.dailyStreak(LocalDate.now().toEpochDay());
            case "active" -> (long)data.active().size();
            case "active_story" -> (long)plugin.questManager().activeCount(data,QuestCategory.STORY);
            case "active_side" -> (long)plugin.questManager().activeCount(data,QuestCategory.SIDE);
            case "active_daily" -> (long)plugin.questManager().activeCount(data,QuestCategory.DAILY);
            case "npcs_met" -> (long)data.metCount();
            case "active_progress_percent" -> {int[] p=tracked(data);yield p==null||p[1]==0?0L:Math.round(p[0]*100.0/p[1]);}
            default -> null;
        };
    }

    String text(PlayerData data,String key){
        return switch(key){
            case "xp_bar" -> bar(data==null?0:plugin.progression().curve().progress(data.skillXp()));
            case "story_bar" -> {int total=plugin.quests().story().size();yield bar(data==null||total==0?0:storyDone(data)/(double)total);}
            case "chapter_name" -> data==null?"":plugin.quests().chapterName(chapter(data));
            case "next_story" -> {Quest q=data==null?null:plugin.questManager().nextStoryQuest(data);yield q==null?"":Text.plain(Text.mm(q.name()));}
            case "next_story_npc" -> {Quest q=data==null?null:plugin.questManager().nextStoryQuest(data);yield q==null||q.giver().isEmpty()?"":plugin.npcs().name(q.giver());}
            case "story_finished" -> yesNo(data!=null&&!plugin.quests().story().isEmpty()&&plugin.questManager().nextStoryQuest(data)==null);
            case "active_name" -> {Quest q=data==null?null:first(data);yield q==null?"":Text.plain(Text.mm(q.name()));}
            case "active_npc" -> {Quest q=data==null?null:first(data);yield q==null?"":plugin.npcs().name(q.turnIn().isEmpty()?q.giver():q.turnIn());}
            case "active_category" -> {Quest q=data==null?null:first(data);yield q==null?"":Text.capitalize(q.category().name().toLowerCase(Locale.ROOT));}
            case "active_progress" -> {int[] p=data==null?null:tracked(data);yield p==null?"":p[0]+"/"+p[1];}
            case "active_objective" -> {Quest q=data==null?null:first(data);yield q==null||q.objectives().isEmpty()?"":Text.plain(Text.mm(plugin.questManager().objectiveLabel(q.objectives().getFirst())));}
            case "daily_ready" -> yesNo(data!=null&&plugin.questManager().dailyCooldownLeft(data)<=0);
            case "daily_cooldown" -> data==null?"":Text.duration(plugin.questManager().dailyCooldownLeft(data));
            default -> null;
        };
    }

    private int chapterCount(){
        var story=plugin.quests().story();return story.isEmpty()?0:story.getLast().chapter();
    }
    private int storyDone(PlayerData data){
        int done=0;for(Quest q:plugin.quests().story())if(data.isCompleted(q.id()))done++;return done;
    }
    /** The chapter the player is in now; the last chapter once the story is finished. */
    private int chapter(PlayerData data){
        Quest next=plugin.questManager().nextStoryQuest(data);return next!=null?next.chapter():chapterCount();
    }
    /** The quest the tracker shows: story first, then daily, then side. */
    private Quest first(PlayerData data){
        var list=plugin.questManager().activeQuests(data);return list.isEmpty()?null:list.getFirst();
    }
    /** {done, needed} summed over the tracked quest's objectives. */
    private int[] tracked(PlayerData data){
        Quest q=first(data);if(q==null)return null;
        ActiveQuest active=data.active(q.id());if(active==null)return null;
        int done=0,need=0;
        for(int i=0;i<q.objectives().size();i++){int amount=q.objectives().get(i).amount();need+=amount;done+=Math.min(amount,active.get(i));}
        return new int[]{done,need};
    }
    private static String yesNo(boolean value){return value?"yes":"no";}
    private static String bar(double progress){
        int filled=(int)Math.round(Math.max(0,Math.min(1,progress))*10);
        return "■".repeat(filled)+"□".repeat(10-filled);
    }
}
