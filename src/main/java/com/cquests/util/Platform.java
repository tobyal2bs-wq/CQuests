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
}
