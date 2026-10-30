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

        int perPage = settings.indexPerPage;
        int indexPages = Math.max(1, (story.size() + perPage - 1) / perPage);
        int indexStart = active.size() + 1;
        int sidePage = indexStart + indexPages;

        Map<String, Integer> pageOf = new HashMap<>();
        for (int i = 0; i < active.size(); i++) {
            pageOf.put(active.get(i).id(), i + 1);
        }

        List<Component> pages = new ArrayList<>();
        for (Quest quest : active) {
            pages.add(Text.mm(questPage(player, data, quest, indexStart)));
        }
        for (int page = 0; page < indexPages; page++) {
            int from = page * perPage;
            int to = Math.min(story.size(), from + perPage);
            pages.add(Text.mm(indexPage(data, story, from, to, page == 0, pageOf, sidePage)));
        }
        pages.add(Text.mm(sidePageText(player, data, pageOf, indexStart)));

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
        return page.toString();
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
        StringBuilder page = new StringBuilder("<bold>All Quests</bold>\n");
        if (first) {
            int done = 0;
            for (Quest quest : story) {
                if (data.isCompleted(quest.id())) {
                    done++;
                }
            }
            page.append(progressBar(done, story.size())).append("\n\n");
        } else {
            page.append("<dark_gray>").append(from + 1).append('-').append(to).append(" of ").append(story.size()).append("</dark_gray>\n\n");
        }
        for (int i = from; i < to; i++) {
            Quest quest = story.get(i);
            String name = Text.escape(quest.name());
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
        int done = 0;
        for (Quest quest : plugin.quests().all()) {
            if (quest.category() == QuestCategory.SIDE && data.isCompleted(quest.id())) {
                done++;
            }
        }
        page.append("<dark_gray>Done ").append(done).append(" of ").append(plugin.quests().sideCount()).append("</dark_gray>\n\n");
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
