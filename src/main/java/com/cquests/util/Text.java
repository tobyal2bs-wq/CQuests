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
        String input=miniMessage==null?"":miniMessage;
        if(input.indexOf('&')<0&&input.indexOf('§')<0)return MM.deserialize(input);
        String[] names={"black","dark_blue","dark_green","dark_aqua","dark_red","dark_purple","gold","gray","dark_gray","blue","green","aqua","red","light_purple","yellow","white"};
        for(int i=0;i<16;i++)input=input.replaceAll("(?i)[&§]"+Integer.toHexString(i),"<"+names[i]+">");
        input=input.replaceAll("(?i)[&§]#([0-9a-f]{6})","<#$1>")
                .replaceAll("(?i)[&§]l","<bold>").replaceAll("(?i)[&§]o","<italic>")
                .replaceAll("(?i)[&§]n","<underlined>").replaceAll("(?i)[&§]m","<strikethrough>")
                .replaceAll("(?i)[&§]k","<obfuscated>").replaceAll("(?i)[&§]r","<reset>");
        return MM.deserialize(input);
    }

    private static final java.util.regex.Pattern TWO_STOPS = java.util.regex.Pattern.compile("<gradient:#([0-9a-fA-F]{6}):#([0-9a-fA-F]{6})>");

    /** A two-colour name gradient gets a bright middle stop, so the name reads as lit rather than a flat fade. */
    public static String shine(String name) {
        if (name == null) return "";
        java.util.regex.Matcher m = TWO_STOPS.matcher(name);
        StringBuilder out = new StringBuilder();
        while (m.find()) {
            int a = Integer.parseInt(m.group(1), 16), b = Integer.parseInt(m.group(2), 16), mid = 0;
            for (int sh = 16; sh >= 0; sh -= 8) {
                int avg = (((a >> sh) & 255) + ((b >> sh) & 255)) / 2;
                mid |= Math.min(255, avg + (255 - avg) * 55 / 100) << sh;
            }
            m.appendReplacement(out, String.format("<gradient:#%s:#%06x:#%s>", m.group(1), mid, m.group(2)));
        }
        return m.appendTail(out).toString();
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
        if (hours > 0) {
            return minutes > 0 ? hours + "h " + minutes + "m" : hours + "h";
        }
        return minutes + "m";
    }
    /** 999, 1.2K, 34.5K, 1.2M, 3B. */
    public static String compact(long n){
        if(n<0)return "-"+compact(n==Long.MIN_VALUE?Long.MAX_VALUE:-n);
        if(n<1000)return Long.toString(n);
        String[] units={"K","M","B","T","Q"};
        double value=n;int unit=-1;
        while(value>=1000&&unit<units.length-1){value/=1000;unit++;}
        String text=value>=100?Long.toString((long)value):String.format(Locale.ROOT,"%.1f",Math.floor(value*10)/10);
        if(text.endsWith(".0"))text=text.substring(0,text.length()-2);
        return text+units[unit];
    }
}
