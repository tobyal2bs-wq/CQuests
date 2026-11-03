package com.cquests.integration;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

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
}
