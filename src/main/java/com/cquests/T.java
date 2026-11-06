package com.cquests;

import org.bukkit.configuration.ConfigurationSection;

/**
 * Every text that used to be written into the code, looked up in messages.yml under text: so it can be
 * changed. The code keeps the English line as the fallback. Placeholders are written as {@code <name>} and
 * filled in here, before the line is read as MiniMessage.
 */
public final class T {
    private T() {}

    private static volatile ConfigurationSection lines;

    /** Called whenever messages.yml is (re)loaded. */
    public static void load(ConfigurationSection messages) { lines = messages == null ? null : messages.getConfigurationSection("text"); }

    public static String t(String key, String fallback, Object... pairs) {
        ConfigurationSection l = lines;
        String s = l == null ? fallback : l.getString(key, fallback);
        for (int i = 0; i + 1 < pairs.length; i += 2) s = s.replace("<" + pairs[i] + ">", String.valueOf(pairs[i + 1]));
        return s;
    }
}
