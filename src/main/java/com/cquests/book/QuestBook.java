package com.cquests.book;

import com.cquests.CQuestsPlugin;
import com.cquests.Settings;
import com.cquests.data.ActiveQuest;
import com.cquests.data.PlayerData;
import com.cquests.model.NpcDef;
import com.cquests.model.Objective;
import com.cquests.model.Quest;
import com.cquests.model.QuestCategory;
import com.cquests.quest.QuestManager;
import com.cquests.util.Text;
import net.kyori.adventure.inventory.Book;
import net.kyori.adventure.text.Component;
import org.bukkit.entity.Player;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * The quest journal, laid out like the reference screenshots:
 * one page per active quest, then the "All Quests" index with a progress bar, then side quests and the daily.
 * Only plain text, colours and page links are used, so Geyser renders it fine for Bedrock players
 * (they just turn pages instead of clicking links).
 */
public final class QuestBook {

    private final CQuestsPlugin plugin;

    public QuestBook(CQuestsPlugin plugin) {
        this.plugin = plugin;
    }

    public void open(Player player) {
        player.openBook(build(player));
    }

    public Book build(Player player) {
        Settings settings = plugin.settings();
        QuestManager qm = plugin.questManager();
        PlayerData data = qm.data(player);
        List<Quest> active = qm.activeQuests(data);
        List<Quest> story = plugin.quests().story();

        // Index pages never mix chapters: each chapter starts on a fresh page with its own heading.
        int perPage = Math.min(3,settings.indexPerPage);
        List<int[]> slices = new ArrayList<>();
        int from = 0;
        while (from < story.size()) {
            int to = from;
            // The first page also carries the title and progress bar, so it lists one quest fewer.
            int limit = slices.isEmpty() ? Math.max(1, perPage - 1) : perPage;
            while (to < story.size() && to - from < limit && story.get(to).chapter() == story.get(from).chapter()) {
                to++;
            }
            slices.add(new int[]{from, to});
            from = to;
        }
        if (slices.isEmpty()) {
            slices.add(new int[]{0, 0});
        }
        List<List<List<String>>> groups=new ArrayList<>();
        int activePages=0;
        for(Quest quest:active){
            List<String> rows=new ArrayList<>();
            rows.add(quest.name());rows.add("Wayfarer level "+Math.max(1,quest.level()));
            if(quest.description()!=null&&!quest.description().isBlank())rows.add(qm.fill(quest.description(),player));
            ActiveQuest progress=data.active(quest.id());
            for(int i=0;i<quest.objectives().size();i++){
                var objective=quest.objectives().get(i);
                rows.add(qm.objectiveLabel(objective)+" "+(progress==null?0:progress.get(i))+"/"+objective.amount());
            }
            rows.add("Rewards:");rows.addAll(qm.rewardLines(quest.reward()));
            var group=com.cquests.dialogue.DialogueView.paginate(rows,18,9);groups.add(group);activePages+=group.size();
        }
        int indexStart = activePages + 2;
        int sidePage = indexStart + slices.size();

        Map<String, Integer> pageOf = new HashMap<>();
        int pageCursor=2;
        for (int i = 0; i < active.size(); i++) {pageOf.put(active.get(i).id(),pageCursor);pageCursor+=groups.get(i).size();}

        List<Component> pages = new ArrayList<>();
        Quest next=qm.nextStoryQuest(data);
        String nextName=next==null?"":next.name().length()>20?next.name().substring(0,19)+"…":next.name();
        String heading="<black><bold>Journey Journal</bold>\n\nLevel "+plugin.progression().level(data)
                +"\n"+plugin.progression().curve().remaining(data.skillXp())+" XP to next level\n\n"
                +(next==null?"Journey complete.":"Next: "+Text.escape(nextName)+"\nRequired level "+Math.max(1,next.level()))+"\n\n"
                +link(indexStart,"<dark_blue>[Story chapters]</dark_blue>")+"\n"
                +(active.isEmpty()?"":link(2,"<dark_blue>[Active quests]</dark_blue>")+"\n")
                +"<click:run_command:'/quests settings'><dark_blue>[Settings]</dark_blue></click>";
        pages.add(Text.mm(heading));
        for(var group:groups)for(var chunk:group)
            pages.add(Text.mm("<black>"+Text.escape(String.join("\n",chunk))+"\n\n"+link(indexStart,"<dark_blue>Story chapters ›</dark_blue>")));
        for (int i = 0; i < slices.size(); i++) {
            pages.add(Text.mm("<black>"+indexPage(data, story, slices.get(i)[0], slices.get(i)[1], i == 0, pageOf, sidePage)));
        }
        pages.add(Text.mm("<black>"+sidePageText(player, data, pageOf, indexStart)));

        return Book.book(Text.mm(settings.bookTitle), Text.mm(settings.bookAuthor), pages);
    }

    private String questPage(Player player, PlayerData data, Quest quest, int indexPage) {
        QuestManager qm = plugin.questManager();
        ActiveQuest active = data.active(quest.id());
        StringBuilder page = new StringBuilder();
        page.append("<bold>").append(Text.escape(quest.name())).append("</bold>\n");
        page.append("<dark_gray>Level ").append(quest.level()).append(" · </dark_gray>").append(status(quest, active)).append("\n\n");

        boolean ready = active != null && qm.ready(quest, active);
        if (ready && !quest.turnIn().isEmpty()) {
            page.append("Return to ").append(plugin.npcs().mention(quest.turnIn())).append(" to claim your reward.\n\n");
        } else if (quest.description() != null && !quest.description().isBlank()) {
            page.append(qm.fill(quest.description(), player)).append("\n\n");
        }

        boolean showList = quest.objectives().size() > 1 || quest.objectives().get(0).amount() > 1
                || quest.description() == null || quest.description().isBlank();
        if (showList && active != null) {
            for (int i = 0; i < quest.objectives().size(); i++) {
                Objective objective = quest.objectives().get(i);
                boolean done = qm.objectiveDone(quest, active, i);
                page.append(done ? "<dark_green>✔</dark_green> " : "<dark_gray>▪</dark_gray> ")
                        .append(qm.objectiveLabel(objective));
                if (objective.amount() > 1) {
                    page.append(done ? " <dark_green>" : " <gold>").append(active.get(i)).append('/').append(objective.amount())
                            .append(done ? "</dark_green>" : "</gold>");
                }
                page.append('\n');
            }
            page.append('\n');
        }
        page.append(link(indexPage, "<dark_gray>« All quests</dark_gray>"));
        return "<black>"+page;
    }

    private String status(Quest quest, ActiveQuest active) {
        if (active == null) {
            return "<dark_gray>Not started</dark_gray>";
        }
        if (plugin.questManager().ready(quest, active)) {
            return "<dark_green>Ready</dark_green>";
        }
        return active.untouched() ? "<blue>New</blue>" : "<gold>In progress</gold>";
    }

    private String indexPage(PlayerData data, List<Quest> story, int from, int to, boolean first,
                             Map<String, Integer> pageOf, int sidePage) {
        QuestManager qm = plugin.questManager();
        StringBuilder page = new StringBuilder();
        if (first) {
            int done = 0;
            for (Quest quest : story) {
                if (data.isCompleted(quest.id())) {
                    done++;
                }
            }
            page.append("<bold>All Quests</bold>\n").append(progressBar(done, story.size())).append('\n');
        }
        if (from < to) {
            int chapter = story.get(from).chapter();
            String name = plugin.quests().chapterName(chapter);
            page.append(first ? "<dark_gray>" : "<bold>").append("Chapter ").append(chapter)
                    .append(first ? "" : "</bold>\n<dark_gray>");
            if (!name.isEmpty()) {
                page.append(first ? " · " : "").append(Text.escape(name));
            }
            page.append("</dark_gray>\n\n");
        }
        for (int i = from; i < to; i++) {
            Quest quest = story.get(i);
            String plain=quest.name();
            String name = Text.escape(plain.length()>23?plain.substring(0,22)+"…":plain);
            String line = switch (qm.state(data, quest)) {
                case COMPLETED -> "<dark_green>✔</dark_green> " + name;
                case ACTIVE, READY -> "<blue>○</blue> " + name;
                case AVAILABLE -> "<blue>○</blue> <dark_gray>" + name + "</dark_gray>";
                case LOCKED -> "<gray>✖ " + name + "</gray>";
            };
            Integer target = pageOf.get(quest.id());
            page.append(target != null ? link(target, line) : line).append('\n');
        }
        if (first) {
            page.append('\n').append(link(sidePage, "<dark_gray>Side quests »</dark_gray>"));
        }
        return page.toString();
    }

    private String progressBar(int done, int total) {
        int length = plugin.settings().barLength;
        int percent = total == 0 ? 100 : (int) Math.floor(done * 100.0 / total);
        int filled = total == 0 ? length : (int) Math.round(length * done / (double) total);
        return "<dark_gray>[</dark_gray><dark_green>" + "|".repeat(filled) + "</dark_green><gray>"
                + "|".repeat(length - filled) + "</gray><dark_gray>]</dark_gray> <bold>" + percent + "%</bold>";
    }

    private String sidePageText(Player player, PlayerData data, Map<String, Integer> pageOf, int indexPage) {
        QuestManager qm = plugin.questManager();
        StringBuilder page = new StringBuilder("<bold>Side Quests</bold>\n");
        page.append("<dark_gray>").append(String.format(Locale.ROOT, "%,d", data.totalSideDone())).append(" jobs completed</dark_gray>\n\n");
        int shown = 0;
        for (Quest quest : qm.activeQuests(data)) {
            if (quest.category() == QuestCategory.SIDE) {
                page.append(link(pageOf.getOrDefault(quest.id(), indexPage), "<blue>○</blue> " + Text.escape(quest.name()))).append('\n');
                shown++;
            }
        }
        if (shown == 0) {
            page.append("<dark_gray>None right now. Villagers you finished a story quest for have more work.</dark_gray>\n");
        }

        NpcDef dailyNpc = plugin.npcs().get(plugin.settings().dailyNpc);
        if (dailyNpc != null) {
            page.append("\n<bold>Daily</bold>\n");
            Quest daily = null;
            for (Quest quest : qm.activeQuests(data)) {
                if (quest.category() == QuestCategory.DAILY) {
                    daily = quest;
                }
            }
            long left = qm.dailyCooldownLeft(data);
            if (daily != null) {
                page.append(link(pageOf.getOrDefault(daily.id(), indexPage), "<blue>○</blue> " + Text.escape(daily.name())));
            } else if (left > 0) {
                page.append("<dark_gray>Next daily in ").append(Text.duration(left)).append("</dark_gray>");
            } else {
                page.append("Visit ").append(plugin.npcs().mention(dailyNpc.id())).append(" for today's job.");
            }
            page.append('\n');
        }
        page.append('\n').append(link(indexPage, "<dark_gray>« All quests</dark_gray>"));
        return qm.fill(page.toString(), player);
    }

    private static String link(int page, String text) {
        return "<click:change_page:'" + page + "'>" + text + "</click>";
    }
}
