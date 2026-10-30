package com.cquests.util;

import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.minimessage.MiniMessage;
import net.kyori.adventure.text.serializer.plain.PlainTextComponentSerializer;

import java.util.Locale;

public final class Text {

    private static final MiniMessage MM = MiniMessage.miniMessage();

    private Text() {
    }

    public static Component mm(String miniMessage) {
        return MM.deserialize(miniMessage == null ? "" : miniMessage);
    }

    public static String escape(String raw) {
        return MM.escapeTags(raw);
    }

    public static String plain(Component component) {
        return PlainTextComponentSerializer.plainText().serialize(component);
    }

    /** ZOMBIE_VILLAGER -> "zombie villager". */
    public static String pretty(String enumName) {
        return enumName.toLowerCase(Locale.ROOT).replace('_', ' ');
    }

    public static String capitalize(String text) {
        StringBuilder out = new StringBuilder(text.length());
        boolean up = true;
        for (char c : text.toCharArray()) {
            out.append(up ? Character.toUpperCase(c) : c);
            up = c == ' ';
        }
        return out.toString();
    }

    public static String plural(String singular) {
        if (singular.endsWith("s") || singular.endsWith("sh") || singular.endsWith("ch") || singular.endsWith("x")) {
            return singular.endsWith("s") ? singular : singular + "es";
        }
        if (singular.endsWith("f")) {
            return singular.substring(0, singular.length() - 1) + "ves";
        }
        if (singular.endsWith("y") && singular.length() > 1 && "aeiou".indexOf(singular.charAt(singular.length() - 2)) < 0) {
            return singular.substring(0, singular.length() - 1) + "ies";
        }
        return singular + "s";
    }

    public static String formatMoney(long amount) {
        if (amount >= 1000 && amount % 1000 == 0) {
            return (amount / 1000) + "k";
        }
        if (amount >= 1000 && amount % 100 == 0) {
            return String.format(Locale.ROOT, "%.1fk", amount / 1000.0);
        }
        return Long.toString(amount);
    }

    public static String duration(long millis) {
        long minutes = Math.max(0, millis) / 60_000L;
        long hours = minutes / 60;
        minutes %= 60;
        return hours > 0 ? hours + "h " + minutes + "m" : minutes + "m";
    }
}
