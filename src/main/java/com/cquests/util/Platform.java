package com.cquests.util;

import org.bukkit.Bukkit;
import org.bukkit.entity.Player;

import java.lang.reflect.Method;
import java.util.UUID;

/** Detects Bedrock (Geyser/Floodgate) players without a hard dependency on Floodgate. */
public final class Platform {

    private static Object floodgateApi;
    private static Method isFloodgatePlayer;

    private Platform() {
    }

    public static void init() {
        floodgateApi = null;
        isFloodgatePlayer = null;
        if (Bukkit.getPluginManager().getPlugin("floodgate") == null) {
            return;
        }
        try {
            Class<?> api = Class.forName("org.geysermc.floodgate.api.FloodgateApi");
            floodgateApi = api.getMethod("getInstance").invoke(null);
            isFloodgatePlayer = api.getMethod("isFloodgatePlayer", UUID.class);
        } catch (ReflectiveOperationException | LinkageError ignored) {
            floodgateApi = null;
        }
    }

    public static boolean isBedrock(Player player) {
        if (floodgateApi != null) {
            try {
                return (boolean) isFloodgatePlayer.invoke(floodgateApi, player.getUniqueId());
            } catch (ReflectiveOperationException ignored) {
                // fall through to the UUID heuristic
            }
        }
        // Floodgate gives Bedrock players UUIDs whose most significant bits are zero.
        return player.getUniqueId().getMostSignificantBits() == 0L;
    }

    /** A new server can also host older clients through ViaVersion; those need the book/menu fallback. */
    public static boolean supportsDialogs(Player player) {
        if (isBedrock(player)) return false;
        var via = Bukkit.getPluginManager().getPlugin("ViaVersion");
        if (via == null || !via.isEnabled()) return true;
        try {
            Class<?> version = Class.forName("com.viaversion.viaversion.api.protocol.version.ProtocolVersion");
            Object api = Class.forName("com.viaversion.viaversion.api.Via").getMethod("getAPI").invoke(null);
            Object client = Class.forName("com.viaversion.viaversion.api.ViaAPI")
                    .getMethod("getPlayerProtocolVersion", UUID.class).invoke(api, player.getUniqueId());
            Object firstDialogClient = version.getField("v1_21_6").get(null);
            return (boolean) version.getMethod("newerThanOrEqualTo", version).invoke(client, firstDialogClient);
        } catch (ReflectiveOperationException | RuntimeException | LinkageError e) {
            return false;
        }
    }
}
