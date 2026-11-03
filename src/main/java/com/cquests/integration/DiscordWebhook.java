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
        post("chapter-complete", "📖 **<player>** finished Chapter <chapter>: <name>", 0x55FFFF,
                player.getName(), "<chapter>", Integer.toString(chapter), "<name>", chapterName);
    }

    public void journeyFinished(Player player) {
        post("journey-finished", "🏆 **<player>** finished the whole journey on <server>!", 0xFFAA00, player.getName(), "<server>", plugin.settings().serverName);
    }

    public void bossDefeated(Player player, String boss) {
        post("boss-defeated", "⚔️ **<player>** defeated **<boss>**!", 0xFF5555, player.getName(), "<boss>", boss);
    }

    public void dailyStreak(Player player, int days) {
        post("daily-streak", "🔥 **<player>** is on a <days>-day daily quest streak!", 0xFF8800, player.getName(), "<days>", Integer.toString(days));
    }

    /** @param pairs placeholder, value, placeholder, value ... */
    private void post(String event, String fallback, int color, String player, String... pairs) {
        String target = url;
        ConfigurationSection c = config;
        if (target.isEmpty() || c == null || !c.getBoolean("events." + event, true)) return;
        String text = c.getString("messages." + event, fallback).replace("<player>", clean(player));
        for (int i = 0; i + 1 < pairs.length; i += 2) text = text.replace(pairs[i], clean(pairs[i + 1]));
        JsonObject embed = new JsonObject();
        embed.addProperty("description", text.length() > 4000 ? text.substring(0, 4000) : text);
        embed.addProperty("color", color);
        JsonArray embeds = new JsonArray();
        embeds.add(embed);
        JsonObject body = new JsonObject();
        body.addProperty("username", c.getString("username", plugin.settings().serverName + " Quests"));
        String avatar = c.getString("avatar-url", "");
        if (avatar.startsWith("https://")) body.addProperty("avatar_url", avatar);
        body.add("embeds", embeds);
        JsonObject mentions = new JsonObject();
        mentions.add("parse", new JsonArray()); // never ping @everyone or roles, whatever a name contains
        body.add("allowed_mentions", mentions);
        String json = body.toString();
        try {
            sender.execute(() -> send(target, json));
        } catch (RuntimeException ignored) {
            // shutting down
        }
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
