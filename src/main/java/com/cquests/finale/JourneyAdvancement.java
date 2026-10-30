package com.cquests.finale;

import com.cquests.CQuestsPlugin;
import com.cquests.util.Text;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import org.bukkit.Bukkit;
import org.bukkit.NamespacedKey;
import org.bukkit.advancement.Advancement;
import org.bukkit.advancement.AdvancementProgress;
import org.bukkit.entity.Player;

import java.io.File;
import java.io.IOException;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.logging.Level;

/**
 * The custom "Finished the Journey" advancement. It is loaded straight into the server at startup;
 * if this server version refuses that, a small datapack is written into the main world instead,
 * which the server picks up on its next restart.
 */
public final class JourneyAdvancement {

    private final CQuestsPlugin plugin;
    private final NamespacedKey key;

    public JourneyAdvancement(CQuestsPlugin plugin) {
        this.plugin = plugin;
        this.key = new NamespacedKey(plugin, "finished_the_journey");
    }

    public void register() {
        if (Bukkit.getAdvancement(key) != null) {
            return;
        }
        String json = json();
        try {
            Object unsafe = Bukkit.getUnsafe();
            Method load = unsafe.getClass().getMethod("loadAdvancement", NamespacedKey.class, String.class);
            load.invoke(unsafe, key, json);
        } catch (ReflectiveOperationException | RuntimeException | LinkageError ignored) {
            // fall back to the datapack below
        }
        if (Bukkit.getAdvancement(key) == null) {
            writeDatapack(json);
        }
    }

    public void award(Player player) {
        Advancement advancement = Bukkit.getAdvancement(key);
        if (advancement == null) {
            register();
            advancement = Bukkit.getAdvancement(key);
        }
        if (advancement == null) {
            plugin.send(player, "<gold>★ Achievement unlocked: <yellow>[" + Text.escape(plugin.settings().advancementTitle) + "]");
            return;
        }
        AdvancementProgress progress = player.getAdvancementProgress(advancement);
        for (String criterion : progress.getRemainingCriteria()) {
            progress.awardCriteria(criterion);
        }
    }

    private String json() {
        JsonObject icon = new JsonObject();
        icon.addProperty("id", "minecraft:nether_star");
        JsonObject title = new JsonObject();
        title.addProperty("text", plugin.settings().advancementTitle);
        title.addProperty("color", "gold");
        JsonObject description = new JsonObject();
        description.addProperty("text", plugin.settings().advancementDescription);

        JsonObject display = new JsonObject();
        display.add("icon", icon);
        display.add("title", title);
        display.add("description", description);
        display.addProperty("frame", "challenge");
        display.addProperty("show_toast", true);
        display.addProperty("announce_to_chat", true);
        display.addProperty("hidden", false);

        JsonObject trigger = new JsonObject();
        trigger.addProperty("trigger", "minecraft:impossible");
        JsonObject criteria = new JsonObject();
        criteria.add("journey", trigger);
        JsonArray requirement = new JsonArray();
        requirement.add("journey");
        JsonArray requirements = new JsonArray();
        requirements.add(requirement);

        JsonObject root = new JsonObject();
        root.addProperty("parent", "minecraft:adventure/root");
        root.add("display", display);
        root.add("criteria", criteria);
        root.add("requirements", requirements);
        return root.toString();
    }

    private void writeDatapack(String json) {
        File pack = new File(Bukkit.getWorlds().get(0).getWorldFolder(), "datapacks/cquests");
        File target = new File(pack, "data/" + key.getNamespace() + "/advancement/" + key.getKey() + ".json");
        try {
            Files.createDirectories(target.getParentFile().toPath());
            Files.writeString(target.toPath(), json, StandardCharsets.UTF_8);
            Files.writeString(new File(pack, "pack.mcmeta").toPath(),
                    "{\"pack\":{\"pack_format\":61,\"supported_formats\":{\"min_inclusive\":48,\"max_inclusive\":999},"
                            + "\"description\":\"CQuests advancements\"}}", StandardCharsets.UTF_8);
            plugin.getLogger().info("Wrote the 'Finished the Journey' advancement datapack; it loads after the next restart.");
        } catch (IOException e) {
            plugin.getLogger().log(Level.WARNING, "Could not write the advancement datapack", e);
        }
    }
}
