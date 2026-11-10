package com.cbosses;

/**
 * Every text players and admins see, looked up in messages.yml under text: so it can be changed. The code
 * keeps the English line as the fallback. Placeholders are written as {@code <name>} and filled in here,
 * before the line is read as MiniMessage.
 */
public final class T {
    private T() {}

    /** The line for key (or the fallback), with each name/value pair filled in. */
    public static String t(String key, String fallback, Object... pairs) {
        CBossesPlugin p = CBossesPlugin.instance();
        String s = p == null ? fallback : p.msg("text." + key, fallback);
        for (int i = 0; i + 1 < pairs.length; i += 2) s = s.replace("<" + pairs[i] + ">", String.valueOf(pairs[i + 1]));
        return s;
    }
}
