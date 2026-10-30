package com.cquests.npc;

import org.bukkit.NamespacedKey;
import org.bukkit.entity.Entity;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.Plugin;

/** Marks our villagers through persistent data so every listener can recognise them. */
public final class NpcTag {

    private static NamespacedKey key;

    private NpcTag() {
    }

    public static void init(Plugin plugin) {
        key = new NamespacedKey(plugin, "npc");
    }

    public static void tag(Entity entity, String npcId) {
        entity.getPersistentDataContainer().set(key, PersistentDataType.STRING, npcId);
    }

    public static String npcId(Entity entity) {
        return entity.getPersistentDataContainer().get(key, PersistentDataType.STRING);
    }

    public static boolean isNpc(Entity entity) {
        return entity.getPersistentDataContainer().has(key, PersistentDataType.STRING);
    }
}
