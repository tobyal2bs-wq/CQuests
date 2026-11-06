package com.cquests.invite;

import com.cquests.T;

import com.cquests.CQuestsPlugin;
import com.cquests.util.Sched;
import com.cquests.util.Text;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.OfflinePlayer;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;

import java.io.File;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;

/**
 * Invite a friend: a new player types /quests invitedby <name> within their first hours. The new
 * player is paid straight away; the friend who invited them is paid once the newcomer finishes the
 * tutorial quest, so an empty alt account earns nothing. Same-IP invites are refused.
 */
public final class InviteService {
    private record Invite(UUID by, String name, long at, boolean paid) {}

    private final CQuestsPlugin plugin;
    private final File file;
    private final Map<UUID, Invite> invited = new HashMap<>();
    private final Map<UUID, Integer> counts = new HashMap<>();

    public InviteService(CQuestsPlugin plugin) {
        this.plugin = plugin;
        this.file = new File(plugin.getDataFolder(), "invites.yml");
        load();
    }

    private synchronized void load() {
        invited.clear(); counts.clear();
        YamlConfiguration yaml = YamlConfiguration.loadConfiguration(file);
        ConfigurationSection inv = yaml.getConfigurationSection("invited");
        if (inv != null) for (String key : inv.getKeys(false)) try {
            invited.put(UUID.fromString(key), new Invite(UUID.fromString(inv.getString(key + ".by", "")), inv.getString(key + ".name", "?"),
                    inv.getLong(key + ".at"), inv.getBoolean(key + ".paid")));
        } catch (IllegalArgumentException ignored) { }
        ConfigurationSection c = yaml.getConfigurationSection("counts");
        if (c != null) for (String key : c.getKeys(false)) try { counts.put(UUID.fromString(key), c.getInt(key)); } catch (IllegalArgumentException ignored) { }
    }

    private synchronized void save() {
        YamlConfiguration yaml = new YamlConfiguration();
        invited.forEach((id, i) -> {
            yaml.set("invited." + id + ".by", i.by().toString()); yaml.set("invited." + id + ".name", i.name());
            yaml.set("invited." + id + ".at", i.at()); yaml.set("invited." + id + ".paid", i.paid());
        });
        counts.forEach((id, n) -> yaml.set("counts." + id, n));
        String text = yaml.saveToString();
        Sched.async(() -> {
            synchronized (file) {
                try { java.nio.file.Files.writeString(file.toPath(), text); }
                catch (IOException e) { plugin.getLogger().warning("Could not save invites.yml: " + e.getMessage()); }
            }
        });
    }

    public boolean enabled() { return plugin.getConfig().getBoolean("invites.enabled", true); }
    public synchronized int count(UUID id) { return counts.getOrDefault(id, 0); }
    public synchronized String invitedBy(UUID id) { Invite i = invited.get(id); return i == null ? null : i.name(); }

    private static String ip(Player p) {
        InetSocketAddress a = p.getAddress();
        return a == null || a.getAddress() == null ? "" : a.getAddress().getHostAddress();
    }

    /** /quests invitedby <name>, run by the new player. */
    public void claim(Player player, String name) {
        if (!enabled()) { plugin.send(player, T.t("invite-service.invites-are-switched-off-on", "<gray>Invites are switched off on this server.")); return; }
        if (name == null || name.isBlank()) { plugin.send(player, T.t("invite-service.quests-invitedby-tell-us-who", "<yellow>/quests invitedby <name></yellow> <gray>Tell us who brought you here and you both get a reward.")); return; }
        long hours = Math.max(1, plugin.getConfig().getLong("invites.window-hours", 48));
        long first = player.getFirstPlayed();
        if (first > 0 && System.currentTimeMillis() - first > hours * 3_600_000L) { plugin.send(player, T.t("invite-service.invites-can-only-be-claimed", "<gray>Invites can only be claimed in your first <hours> hours on the server.", "hours", hours)); return; }
        OfflinePlayer friend = Bukkit.getOfflinePlayerIfCached(name);
        if (friend == null || (!friend.hasPlayedBefore() && !friend.isOnline())) { plugin.send(player, T.t("invite-service.nobody-called-has-played-here", "<red>Nobody called <name> has played here.", "name", Text.escape(name))); return; }
        if (friend.getUniqueId().equals(player.getUniqueId())) { plugin.send(player, T.t("invite-service.you-can-t-invite-yourself", "<red>You can't invite yourself.")); return; }
        Player online = friend.getPlayer();
        if (online != null && !ip(online).isEmpty() && ip(online).equals(ip(player)) && !plugin.getConfig().getBoolean("invites.allow-same-ip", false)) {
            plugin.send(player, T.t("invite-service.you-and-are-on-the", "<red>You and <name> are on the same connection, so this invite doesn't count.", "name", Text.escape(name))); return;
        }
        synchronized (this) {
            if (invited.containsKey(player.getUniqueId())) { plugin.send(player, T.t("invite-service.you-already-said-invited-you", "<gray>You already said <name> invited you.", "name", Text.escape(invited.get(player.getUniqueId()).name()))); return; }
            invited.put(player.getUniqueId(), new Invite(friend.getUniqueId(), friend.getName() == null ? name : friend.getName(), System.currentTimeMillis(), false));
        }
        save();
        pay(player, player.getName(), "invites.new-player");
        String tutorial = plugin.getConfig().getString("quests.tutorial-quest", "tutorial");
        plugin.send(player, T.t("invite-service.welcome-will-get-their-reward", "<gold>Welcome! <white><name></white> <gray>will get their reward when you finish <tutorial>", "name", Text.escape(name), "tutorial", (tutorial == null || tutorial.isBlank() || plugin.quests().get(tutorial) == null ? "your first quest." : "the tutorial.")));
        if (online != null) Sched.entity(online, () -> plugin.send(online, T.t("invite-service.says-you-invited-them-you", "<gold><player> <gray>says you invited them! You get your reward when they finish the tutorial.", "player", Text.escape(player.getName()))));
        if (alreadyDone(player)) onTutorialDone(player);
    }

    private boolean alreadyDone(Player player) {
        String tutorial = plugin.getConfig().getString("quests.tutorial-quest", "tutorial");
        String quest = tutorial == null || tutorial.isBlank() || plugin.quests().get(tutorial) == null ? plugin.settings().welcomeQuest : tutorial;
        return plugin.questManager().data(player).isCompleted(quest);
    }

    /** Called when a player finishes the tutorial (or the welcome quest when there is no tutorial). Pays their inviter once. */
    public void onTutorialDone(Player player) {
        Invite invite;
        int total;
        synchronized (this) {
            invite = invited.get(player.getUniqueId());
            if (invite == null || invite.paid()) return;
            invited.put(player.getUniqueId(), new Invite(invite.by(), invite.name(), invite.at(), true));
            total = counts.merge(invite.by(), 1, Integer::sum);
        }
        save();
        pay(Bukkit.getPlayer(invite.by()), invite.name(), "invites.inviter");
        Player friend = Bukkit.getPlayer(invite.by());
        if (friend != null) Sched.entity(friend, () -> plugin.send(friend, T.t("invite-service.finished-the-tutorial-thanks-for", "<gold>★ <player> <gray>finished the tutorial. Thanks for inviting them! <white>Friends invited: <total>", "player", Text.escape(player.getName()), "total", total)));
        for (String raw : plugin.getConfig().getStringList("invites.milestones." + total)) {
            String command = raw.replace("%player%", invite.name()).replace("<player>", invite.name());
            Sched.global(() -> Bukkit.dispatchCommand(Bukkit.getConsoleSender(), command.startsWith("/") ? command.substring(1) : command));
        }
        if (!plugin.getConfig().getStringList("invites.milestones." + total).isEmpty())
            Sched.global(() -> Bukkit.broadcast(Text.mm(T.t("invite-service.has-invited-friends-to-the", "<gold>★ <name> <gray>has invited <white><total></white> friends to the server!", "name", Text.escape(invite.name()), "total", total))));
    }

    /** Money by name (works offline with most economy plugins); items only when the player is online. */
    private void pay(Player online, String name, String path) {
        long money = plugin.getConfig().getLong(path + ".money");
        String moneyCommand = plugin.settings().moneyCommand;
        if (money > 0 && moneyCommand != null && !moneyCommand.isBlank()) {
            String command = moneyCommand.replace("%player%", name).replace("%amount%", Long.toString(money));
            Sched.global(() -> Bukkit.dispatchCommand(Bukkit.getConsoleSender(), command.startsWith("/") ? command.substring(1) : command));
        }
        for (String raw : plugin.getConfig().getStringList(path + ".commands")) {
            String command = raw.replace("%player%", name).replace("<player>", name);
            Sched.global(() -> Bukkit.dispatchCommand(Bukkit.getConsoleSender(), command.startsWith("/") ? command.substring(1) : command));
        }
        List<String> items = plugin.getConfig().getStringList(path + ".items");
        if (online == null) return;
        Sched.entity(online, () -> {
            for (String line : items) {
                String[] parts = line.trim().split("\\s+");
                Material m = Material.matchMaterial(parts[0]);
                int amount = 1;
                try { if (parts.length > 1) amount = Math.max(1, Math.min(64, Integer.parseInt(parts[1]))); } catch (NumberFormatException ignored) { }
                if (m != null && m.isItem()) online.getInventory().addItem(new ItemStack(m, amount)).values().forEach(left -> online.getWorld().dropItemNaturally(online.getLocation(), left));
            }
            if (money > 0) plugin.send(online, T.t("invite-service.invite-reward", "<green>+<amount></green> <gray>invite reward.", "amount", String.format(Locale.ROOT, "%,d", money)));
        });
    }

    public void show(Player player) {
        String by = invitedBy(player.getUniqueId());
        plugin.send(player, T.t("invite-service.invites-friends-you-invited-who", "<gold>Invites</gold> <gray>Friends you invited who finished the tutorial: <white><getuniqueid><by>", "getuniqueid", count(player.getUniqueId()), "by", (by == null ? "" : "</white> <gray>Invited by: <white>" + Text.escape(by))));
        plugin.send(player, T.t("invite-service.new-players-type-quests-invitedby", "<gray>New players type <yellow>/quests invitedby <player></yellow> and you both get rewards.", "player", Text.escape(player.getName())));
    }

    private java.util.Set<String> milestones() {
        java.util.Set<String> out = new java.util.TreeSet<>();
        var d = plugin.getConfig().getDefaults();
        if (d != null && d.isConfigurationSection("invites.milestones")) out.addAll(d.getConfigurationSection("invites.milestones").getKeys(false));
        if (plugin.getConfig().isConfigurationSection("invites.milestones")) out.addAll(plugin.getConfig().getConfigurationSection("invites.milestones").getKeys(false));
        return out;
    }

    /** /cq test invite: shows both sides' messages and rewards without saving anything. */
    public void test(Player player) {
        plugin.send(player, T.t("invite-service.new-player-sees-welcome-will", "<gray>New player sees: <gold>Welcome! <white><player></white> <gray>will get their reward when they finish the tutorial.", "player", Text.escape(player.getName())));
        plugin.send(player, T.t("invite-service.new-player-gets-money", "<gray>New player gets: <white><money> money <items>", "money", plugin.getConfig().getLong("invites.new-player.money"), "items", plugin.getConfig().getStringList("invites.new-player.items")));
        plugin.send(player, T.t("invite-service.inviter-gets-money-after-the", "<gray>Inviter gets: <white><money> money <items> <gray>after the tutorial. Milestones: <white><milestones>", "money", plugin.getConfig().getLong("invites.inviter.money"), "items", plugin.getConfig().getStringList("invites.inviter.items"), "milestones", String.join(", ", milestones())));
    }
}
