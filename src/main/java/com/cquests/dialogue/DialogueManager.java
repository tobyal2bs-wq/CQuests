package com.cquests.dialogue;

import com.cquests.CQuestsPlugin;
import com.cquests.data.ActiveQuest;
import com.cquests.data.PlayerData;
import com.cquests.model.NpcDef;
import com.cquests.model.Objective;
import com.cquests.model.Quest;
import com.cquests.quest.QuestManager;
import com.cquests.util.Platform;
import com.cquests.util.Sched;
import com.cquests.util.Text;
import org.bukkit.Location;
import org.bukkit.Sound;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Player;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ThreadLocalRandom;

/**
 * What happens when a player right-clicks an NPC: hand-ins first, then progress chatter,
 * then a quest offer. An offer is accepted by clicking the NPC again (works for Bedrock too)
 * or with the clickable [Accept] in chat.
 */
public final class DialogueManager {

    private record Line(boolean speech, String text) {
    }

    private record Pending(String npcId, String questId, long expires) {
    }

    private final CQuestsPlugin plugin;
    private final Set<UUID> talking = ConcurrentHashMap.newKeySet();
    private final Map<UUID, Pending> pending = new ConcurrentHashMap<>();

    public DialogueManager(CQuestsPlugin plugin) {
        this.plugin = plugin;
    }

    private QuestManager qm() {
        return plugin.questManager();
    }

    public void forget(Player player) {
        talking.remove(player.getUniqueId());
        pending.remove(player.getUniqueId());
    }

    public void onClick(Player player, NpcDef npc, Entity entity) {
        if (talking.contains(player.getUniqueId())) {
            return;
        }
        if (plugin.settings().lookAtPlayer) {
            Location eye = player.getEyeLocation();
            Sched.entity(entity, () -> face(entity, eye));
        }
        PlayerData data = qm().data(player);
        List<Line> lines = new ArrayList<>();

        if (data.meet(npc.id())) {
            npc.intro().forEach(text -> lines.add(new Line(true, text)));
            plugin.visibility().refresh(player);
        }

        boolean talked = qm().talk(player, npc.id());
        for (String delivered : qm().deliver(player, npc.id())) {
            lines.add(new Line(false, delivered));
        }

        List<Quest> ready = qm().readyAt(data, npc.id());
        if (!ready.isEmpty()) {
            for (Quest quest : ready) {
                List<String> complete = quest.complete().isEmpty() ? List.of("Well done, {player}!") : quest.complete();
                complete.forEach(text -> lines.add(new Line(true, text)));
            }
            speak(player, npc, lines, () -> ready.forEach(quest -> qm().complete(player, quest)));
            return;
        }

        Quest waiting = qm().pendingAt(data, npc.id());
        if (waiting != null) {
            if (!talked && lines.isEmpty()) {
                lines.add(new Line(true, pick(npc.idle(), "Still working on it? Take your time.")));
            }
            lines.add(new Line(false, progressSummary(data, waiting)));
            speak(player, npc, lines, null);
            return;
        }
        if (talked) {
            speak(player, npc, lines, null);
            return;
        }

        QuestManager.Offer offer = qm().nextOffer(player, npc);
        if (offer.quest() != null) {
            Quest quest = offer.quest();
            Pending previous = pending.get(player.getUniqueId());
            if (previous != null && previous.npcId().equals(npc.id()) && previous.questId().equals(quest.id())
                    && previous.expires() > System.currentTimeMillis() && lines.isEmpty()) {
                pending.remove(player.getUniqueId());
                qm().accept(player, quest);
                return;
            }
            offerLines(quest).forEach(text -> lines.add(new Line(true, text)));
            lines.add(new Line(false, rewardPreview(quest)));
            lines.add(new Line(false, acceptPrompt(player)));
            speak(player, npc, lines, () -> pending.put(player.getUniqueId(),
                    new Pending(npc.id(), quest.id(), System.currentTimeMillis() + plugin.settings().acceptTimeoutMillis)));
            return;
        }

        switch (offer.reason()) {
            case "locked" -> {
                Quest next = qm().nextStoryQuest(data);
                lines.add(new Line(true, plugin.settings().msg("npc-locked", "I'm not ready for you yet, {player}.")));
                if (next != null && !next.giver().isEmpty() && !next.giver().equals(npc.id())) {
                    lines.add(new Line(true, "Go and see {npc:" + next.giver() + "} first."));
                }
            }
            case "too-many" -> lines.add(new Line(true, plugin.settings().msg("npc-too-many",
                    "You've got your hands full. Finish one of your side quests first.")));
            case "daily-cooldown" -> lines.add(new Line(true, plugin.settings().msg("npc-daily-cooldown",
                    "Come back in <time> and I'll have another job for you.")
                    .replace("<time>", Text.duration(qm().dailyCooldownLeft(data)))));
            default -> {
                if (lines.isEmpty()) {
                    lines.add(new Line(true, pick(npc.idle(), "Good to see you, {player}.")));
                }
            }
        }
        speak(player, npc, lines, null);
    }

    /** Called by /quests accept (the clickable chat button). */
    public boolean acceptPending(Player player) {
        Pending offer = pending.remove(player.getUniqueId());
        if (offer == null || offer.expires() < System.currentTimeMillis()) {
            return false;
        }
        NpcDef npc = plugin.npcs().get(offer.npcId());
        Quest quest = plugin.quests().get(offer.questId());
        if (npc == null || quest == null) {
            return false;
        }
        QuestManager.Offer current = qm().nextOffer(player, npc);
        if (current.quest() == null || !current.quest().id().equals(quest.id())) {
            return false;
        }
        return qm().accept(player, quest);
    }

    private List<String> offerLines(Quest quest) {
        if (!quest.offer().isEmpty()) {
            return quest.offer();
        }
        List<String> out = new ArrayList<>();
        for (Objective objective : quest.objectives()) {
            out.add(qm().objectiveSentence(objective));
        }
        return out;
    }

    private String rewardPreview(Quest quest) {
        List<String> rewards = qm().rewardLines(quest.reward());
        String list = rewards.isEmpty() ? "<gray>nothing but thanks" : String.join("<gray>, ", rewards);
        return "<dark_gray>» <gray>Quest: <white><bold>" + Text.escape(quest.name()) + "</bold></white> <dark_gray>(Lv "
                + quest.level() + ")</dark_gray> <gray>Reward: " + list;
    }

    private String acceptPrompt(Player player) {
        String again = plugin.settings().msg("accept-prompt", "<yellow>Click the villager again to accept.");
        if (Platform.isBedrock(player)) {
            return "<dark_gray>» " + again;
        }
        return "<dark_gray>» " + again + " <click:run_command:'/quests accept'><hover:show_text:'<green>Accept quest'>"
                + "<green><bold>[Accept]</bold></green></hover></click>";
    }

    private String progressSummary(PlayerData data, Quest quest) {
        ActiveQuest active = data.active(quest.id());
        StringBuilder out = new StringBuilder("<dark_gray>» <white><bold>" + Text.escape(quest.name()) + "</bold></white>");
        if (active == null) {
            return out.toString();
        }
        for (int i = 0; i < quest.objectives().size(); i++) {
            Objective objective = quest.objectives().get(i);
            boolean done = qm().objectiveDone(quest, active, i);
            out.append("\n  ").append(done ? "<green>✔ " : "<gray>• ").append("<white>").append(qm().objectiveLabel(objective));
            if (objective.amount() > 1) {
                out.append(done ? " <green>" : " <yellow>").append(active.get(i)).append('/').append(objective.amount());
            }
        }
        return out.toString();
    }

    private void speak(Player player, NpcDef npc, List<Line> lines, Runnable after) {
        if (lines.isEmpty()) {
            if (after != null) {
                after.run();
            }
            return;
        }
        talking.add(player.getUniqueId());
        sayLine(player, npc, lines, 0, after);
    }

    private void sayLine(Player player, NpcDef npc, List<Line> lines, int index, Runnable after) {
        Line line = lines.get(index);
        String text = qm().fill(line.text(), player);
        if (line.speech()) {
            player.sendMessage(Text.mm(plugin.settings().npcChatFormat
                    .replace("<name>", Text.escape(npc.name()))
                    .replace("<text>", text)));
            player.playSound(player.getLocation(), Sound.ENTITY_VILLAGER_AMBIENT, 0.6f, 1f);
        } else {
            player.sendMessage(Text.mm(text));
        }
        if (index + 1 >= lines.size()) {
            talking.remove(player.getUniqueId());
            if (after != null) {
                after.run();
            }
            return;
        }
        // Only speech gets a pause; system lines (rewards, prompts) follow right away.
        long delay = lines.get(index + 1).speech() ? plugin.settings().lineDelayTicks : 1;
        player.getScheduler().runDelayed(plugin, t -> sayLine(player, npc, lines, index + 1, after),
                () -> talking.remove(player.getUniqueId()), delay);
    }

    private static void face(Entity entity, Location target) {
        Location from = entity.getLocation();
        double dx = target.getX() - from.getX();
        double dz = target.getZ() - from.getZ();
        float yaw = (float) Math.toDegrees(Math.atan2(-dx, dz));
        entity.setRotation(yaw, 0f);
    }

    private static String pick(List<String> options, String fallback) {
        return options.isEmpty() ? fallback : options.get(ThreadLocalRandom.current().nextInt(options.size()));
    }
}
