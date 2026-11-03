package com.cquests.integration;

import com.cquests.CQuestsPlugin;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.entity.Player;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

/**
 * Posts story moments to a Discord channel webhook (config.yml, discord section). Off while the URL is
 * empty. Sending happens on one background thread with a small bounded queue: a slow or broken
 * Discord never blocks the server, and a flood of events drops the oldest instead of piling up.
 */
public final class DiscordWebhook {
    private final CQuestsPlugin plugin;
    private final HttpClient http = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(5)).build();
    private final ThreadPoolExecutor sender = new ThreadPoolExecutor(1, 1, 30, TimeUnit.SECONDS, new ArrayBlockingQueue<>(64), r -> {
        Thread t = new Thread(r, "CQuests-discord");
        t.setDaemon(true);
        return t;
    }, new ThreadPoolExecutor.DiscardOldestPolicy());
    private volatile String url = "";
    private volatile ConfigurationSection config;
    private volatile long lastSent;
    private volatile boolean warned;

    public DiscordWebhook(CQuestsPlugin plugin) {
        this.plugin = plugin;
        sender.allowCoreThreadTimeOut(true);
        reload();
    }

    public void reload() {
        config = plugin.getConfig().getConfigurationSection("discord");
        String value = config == null ? "" : config.getString("webhook-url", "").trim();
        url = value.startsWith("https://discord.com/api/webhooks/") || value.startsWith("https://discordapp.com/api/webhooks/")
                || value.startsWith("https://ptb.discord.com/api/webhooks/") || value.startsWith("https://canary.discord.com/api/webhooks/") ? value : "";
        if (!value.isEmpty() && url.isEmpty()) plugin.getLogger().warning("discord.webhook-url must be a Discord webhook link (https://discord.com/api/webhooks/...)");
        warned = false;
    }

    public boolean enabled() {
        return !url.isEmpty();
    }

    public void chapterComplete(Player player, int chapter, String chapterName) {
        String next = plugin.quests().chapterName(chapter + 1);
        post(player, "chapter-complete", "📖  Chapter " + chapter + " complete", "**<player>** finished **Chapter <chapter>: <name>**",
                0x3BA7FF, List.of(field("📚 Chapter", chapter + " · " + chapterName),
                        field("➡️ Up next", next.isEmpty() || plugin.settings().lockedChapters.contains(chapter + 1) ? "The story so far is done" : "Chapter " + (chapter + 1) + " · " + next)),
                "<chapter>", Integer.toString(chapter), "<name>", chapterName);
    }

    public void journeyFinished(Player player) {
        post(player, "journey-finished", "🏆  Journey complete", "**<player>** finished the whole journey on <server>!",
                0xFFB020, List.of(field("👣 Days on the road", Long.toString(daysSinceStart(player)))),
                "<server>", plugin.settings().serverName);
    }

    public void bossDefeated(Player player, String boss) {
        post(player, "boss-defeated", "⚔️  Boss defeated", "**<player>** defeated **<boss>**!",
                0xE5484D, List.of(field("💀 Boss", boss)), "<boss>", boss);
    }

    public void dailyStreak(Player player, int days) {
        post(player, "daily-streak", "🔥  " + days + "-day streak", "**<player>** is on a **<days>-day** daily quest streak!",
                0xFF7A1A, List.of(field("🔥 Streak", days + " days in a row")), "<days>", Integer.toString(days));
    }

    record Field(String name, String value) { }
    private static Field field(String name, String value) { return new Field(name, value); }

    private long daysSinceStart(Player player) {
        var data = plugin.store().cached(player.getUniqueId());
        long started = data == null ? 0 : data.startedAt();
        return started <= 0 ? 1 : Math.max(1, (System.currentTimeMillis() - started) / 86_400_000L + 1);
    }

    /** Level and story progress for every embed; read from memory on the player's own thread. */
    private List<Field> stats(Player player) {
        var data = plugin.store().cached(player.getUniqueId());
        if (data == null) return List.of();
        int total = plugin.quests().story().size(), done = 0;
        for (var quest : plugin.quests().story()) if (data.isCompleted(quest.id())) done++;
        int percent = total == 0 ? 0 : (int) Math.round(done * 100.0 / total);
        return List.of(field("⭐ Level", Integer.toString(plugin.progression().level(data))),
                field("📜 Story", done + "/" + total + "  " + bar(percent) + "  " + percent + "%"));
    }

    /** ▰▰▰▰▱▱▱▱▱▱ */
    static String bar(int percent) {
        int filled = Math.max(0, Math.min(10, Math.round(percent / 10f)));
        return "▰".repeat(filled) + "▱".repeat(10 - filled);
    }

    /** @param pairs placeholder, value, placeholder, value ... */
    private void post(Player player, String event, String title, String fallback, int color, List<Field> fields, String... pairs) {
        String target = url;
        ConfigurationSection c = config;
        if (target.isEmpty() || c == null || !c.getBoolean("events." + event, true)) return;
        String text = c.getString("messages." + event, fallback).replace("<player>", clean(player.getName()));
        for (int i = 0; i + 1 < pairs.length; i += 2) text = text.replace(pairs[i], clean(pairs[i + 1]));
        List<Field> all = new ArrayList<>(fields);
        all.addAll(stats(player));
        String json = body(c, player.getName(), player.getUniqueId().toString().replace("-", ""), title, text, color, all).toString();
        try {
            sender.execute(() -> send(target, json));
        } catch (RuntimeException ignored) {
            // shutting down
        }
    }

    JsonObject body(ConfigurationSection c, String playerName, String uuid, String title, String text, int color, List<Field> fields) {
        String server = plugin.settings().serverName;
        JsonObject embed = new JsonObject();
        JsonObject author = new JsonObject();
        author.addProperty("name", playerName);
        String head = c.getString("player-head-url", "https://mc-heads.net/avatar/<uuid>/64").replace("<uuid>", uuid).replace("<player>", playerName);
        if (head.startsWith("https://")) author.addProperty("icon_url", head);
        embed.add("author", author);
        embed.addProperty("title", title);
        embed.addProperty("description", text.length() > 4000 ? text.substring(0, 4000) : text);
        embed.addProperty("color", color);
        JsonArray list = new JsonArray();
        for (Field f : fields) {
            if (f.value() == null || f.value().isBlank()) continue;
            JsonObject o = new JsonObject();
            o.addProperty("name", f.name());
            o.addProperty("value", f.value().length() > 1000 ? f.value().substring(0, 1000) : f.value());
            o.addProperty("inline", true);
            list.add(o);
        }
        if (!list.isEmpty()) embed.add("fields", list);
        String body = c.getString("player-body-url", "https://mc-heads.net/body/<uuid>/128").replace("<uuid>", uuid).replace("<player>", playerName);
        if (body.startsWith("https://")) { JsonObject t = new JsonObject(); t.addProperty("url", body); embed.add("thumbnail", t); }
        String banner = c.getString("banner-url", "");
        if (banner.startsWith("https://")) { JsonObject i = new JsonObject(); i.addProperty("url", banner); embed.add("image", i); }
        JsonObject footer = new JsonObject();
        footer.addProperty("text", server + " • CQuests");
        String icon = c.getString("avatar-url", "");
        if (icon.startsWith("https://")) footer.addProperty("icon_url", icon);
        embed.add("footer", footer);
        embed.addProperty("timestamp", java.time.Instant.now().toString());
        JsonArray embeds = new JsonArray();
        embeds.add(embed);
        JsonObject out = new JsonObject();
        out.addProperty("username", c.getString("username", server + " Quests"));
        if (icon.startsWith("https://")) out.addProperty("avatar_url", icon);
        out.add("embeds", embeds);
        JsonObject mentions = new JsonObject();
        mentions.add("parse", new JsonArray()); // never ping @everyone or roles, whatever a name contains
        out.add("allowed_mentions", mentions);
        return out;
    }

    private void send(String target, String json) {
        try {
            // Discord allows about 30 webhook posts a minute; stay well under it.
            long wait = lastSent + 2000 - System.currentTimeMillis();
            if (wait > 0) Thread.sleep(wait);
            HttpRequest request = HttpRequest.newBuilder(URI.create(target)).timeout(Duration.ofSeconds(10))
                    .header("Content-Type", "application/json").POST(HttpRequest.BodyPublishers.ofString(json)).build();
            HttpResponse<Void> response = http.send(request, HttpResponse.BodyHandlers.discarding());
            lastSent = System.currentTimeMillis();
            if (response.statusCode() >= 300 && !warned) {
                warned = true;
                plugin.getLogger().warning("Discord webhook answered " + response.statusCode() + "; check discord.webhook-url.");
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } catch (Exception e) {
            if (!warned) {
                warned = true;
                plugin.getLogger().warning("Could not reach the Discord webhook: " + e.getMessage());
            }
        }
    }

    /** Player and chapter names can't break the message or the markdown. */
    static String clean(String text) {
        if (text == null) return "";
        return text.replace("@", "@\u200b").replaceAll("([*_`~|>\\\\])", "\\\\$1");
    }

    public void shutdown() {
        sender.shutdown();
        try {
            if (!sender.awaitTermination(3, TimeUnit.SECONDS)) sender.shutdownNow();
        } catch (InterruptedException e) {
            sender.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}
