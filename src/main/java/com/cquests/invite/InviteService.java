package com.cquests.invite;

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
        if (!enabled()) { plugin.send(player, "<gray>Invites are switched off on this server."); return; }
        if (name == null || name.isBlank()) { plugin.send(player, "<yellow>/quests invitedby <name></yellow> <gray>Tell us who brought you here and you both get a reward."); return; }
        long hours = Math.max(1, plugin.getConfig().getLong("invites.window-hours", 48));
        long first = player.getFirstPlayed();
        if (first > 0 && System.currentTimeMillis() - first > hours * 3_600_000L) { plugin.send(player, "<gray>Invites can only be claimed in your first " + hours + " hours on the server."); return; }
        OfflinePlayer friend = Bukkit.getOfflinePlayerIfCached(name);
        if (friend == null || (!friend.hasPlayedBefore() && !friend.isOnline())) { plugin.send(player, "<red>Nobody called " + Text.escape(name) + " has played here."); return; }
        if (friend.getUniqueId().equals(player.getUniqueId())) { plugin.send(player, "<red>You can't invite yourself."); return; }
        Player online = friend.getPlayer();
        if (online != null && !ip(online).isEmpty() && ip(online).equals(ip(player)) && !plugin.getConfig().getBoolean("invites.allow-same-ip", false)) {
            plugin.send(player, "<red>You and " + Text.escape(name) + " are on the same connection, so this invite doesn't count."); return;
        }
        synchronized (this) {
            if (invited.containsKey(player.getUniqueId())) { plugin.send(player, "<gray>You already said " + Text.escape(invited.get(player.getUniqueId()).name()) + " invited you."); return; }
            invited.put(player.getUniqueId(), new Invite(friend.getUniqueId(), friend.getName() == null ? name : friend.getName(), System.currentTimeMillis(), false));
        }
        save();
        pay(player, player.getName(), "invites.new-player");
        String tutorial = plugin.getConfig().getString("quests.tutorial-quest", "tutorial");
        plugin.send(player, "<gold>Welcome! <white>" + Text.escape(name) + "</white> <gray>will get their reward when you finish "
                + (tutorial == null || tutorial.isBlank() || plugin.quests().get(tutorial) == null ? "your first quest." : "the tutorial."));
        if (online != null) Sched.entity(online, () -> plugin.send(online, "<gold>" + Text.escape(player.getName()) + " <gray>says you invited them! You get your reward when they finish the tutorial."));
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
        if (friend != null) Sched.entity(friend, () -> plugin.send(friend, "<gold>★ " + Text.escape(player.getName()) + " <gray>finished the tutorial. Thanks for inviting them! <white>Friends invited: " + total));
        for (String raw : plugin.getConfig().getStringList("invites.milestones." + total)) {
            String command = raw.replace("%player%", invite.name()).replace("<player>", invite.name());
            Sched.global(() -> Bukkit.dispatchCommand(Bukkit.getConsoleSender(), command.startsWith("/") ? command.substring(1) : command));
        }
        if (!plugin.getConfig().getStringList("invites.milestones." + total).isEmpty())
            Sched.global(() -> Bukkit.broadcast(Text.mm("<gold>★ " + Text.escape(invite.name()) + " <gray>has invited <white>" + total + "</white> friends to the server!")));
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
            if (money > 0) plugin.send(online, "<green>+" + String.format(Locale.ROOT, "%,d", money) + "</green> <gray>invite reward.");
        });
    }

    public void show(Player player) {
        String by = invitedBy(player.getUniqueId());
        plugin.send(player, "<gold>Invites</gold> <gray>Friends you invited who finished the tutorial: <white>" + count(player.getUniqueId())
                + (by == null ? "" : "</white> <gray>Invited by: <white>" + Text.escape(by)));
        plugin.send(player, "<gray>New players type <yellow>/quests invitedby " + Text.escape(player.getName()) + "</yellow> and you both get rewards.");
    }

    /** /cq test invite: shows both sides' messages and rewards without saving anything. */
    public void test(Player player) {
        plugin.send(player, "<gray>New player sees: <gold>Welcome! <white>" + Text.escape(player.getName()) + "</white> <gray>will get their reward when they finish the tutorial.");
        plugin.send(player, "<gray>New player gets: <white>" + plugin.getConfig().getLong("invites.new-player.money") + " money " + plugin.getConfig().getStringList("invites.new-player.items"));
        plugin.send(player, "<gray>Inviter gets: <white>" + plugin.getConfig().getLong("invites.inviter.money") + " money " + plugin.getConfig().getStringList("invites.inviter.items")
                + " <gray>after the tutorial. Milestones: <white>" + String.join(", ", plugin.getConfig().isConfigurationSection("invites.milestones")
                ? plugin.getConfig().getConfigurationSection("invites.milestones").getKeys(false) : java.util.Set.of()));
    }
}
