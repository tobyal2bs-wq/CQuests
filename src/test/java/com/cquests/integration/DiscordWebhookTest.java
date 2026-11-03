package com.cquests.integration;

import com.cquests.CQuestsPlugin;
import com.cquests.Settings;
import org.bukkit.configuration.file.YamlConfiguration;
import org.junit.jupiter.api.Test;

import java.io.File;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class DiscordWebhookTest {
    @Test
    void namesCannotPingOrBreakMarkdown() {
        assertEquals("Steve", DiscordWebhook.clean("Steve"));
        assertEquals("\\_cool\\_kid\\_", DiscordWebhook.clean("_cool_kid_"));
        assertEquals("\\*\\*bold\\*\\*", DiscordWebhook.clean("**bold**"));
        assertFalse(DiscordWebhook.clean("@everyone").contains("@everyone"));
        assertFalse(DiscordWebhook.clean("@here").contains("@here"));
        assertEquals("", DiscordWebhook.clean(null));
    }

    @Test
    void progressBar() {
        assertEquals("▱▱▱▱▱▱▱▱▱▱", DiscordWebhook.bar(0));
        assertEquals("▰▰▰▰▰▱▱▱▱▱", DiscordWebhook.bar(50));
        assertEquals("▰▰▰▰▰▰▰▰▰▰", DiscordWebhook.bar(100));
    }

    @Test
    void embedHasPlayerHeadFieldsFooterAndNoPings() {
        var config = YamlConfiguration.loadConfiguration(new File("src/main/resources/config.yml"));
        var plugin = mock(CQuestsPlugin.class);
        when(plugin.getConfig()).thenReturn(config);
        when(plugin.settings()).thenReturn(new Settings(config, new YamlConfiguration()));
        var hook = new DiscordWebhook(plugin);
        try {
            var body = hook.body(config.getConfigurationSection("discord"), "Steve", "abc123", "⚔️  Boss defeated", "**Steve** won",
                    0xE5484D, List.of(new DiscordWebhook.Field("💀 Boss", "The Ravager"), new DiscordWebhook.Field("empty", "")));
            var embed = body.getAsJsonArray("embeds").get(0).getAsJsonObject();
            assertEquals("Steve", embed.getAsJsonObject("author").get("name").getAsString());
            assertEquals("https://mc-heads.net/avatar/abc123/64", embed.getAsJsonObject("author").get("icon_url").getAsString());
            assertEquals("https://mc-heads.net/body/abc123/128", embed.getAsJsonObject("thumbnail").get("url").getAsString());
            assertEquals(1, embed.getAsJsonArray("fields").size(), "blank fields are left out");
            assertTrue(embed.getAsJsonObject("footer").get("text").getAsString().endsWith("• CQuests"));
            assertTrue(embed.has("timestamp"));
            assertEquals(0, body.getAsJsonObject("allowed_mentions").getAsJsonArray("parse").size());
        } finally {
            hook.shutdown();
        }
    }
}
