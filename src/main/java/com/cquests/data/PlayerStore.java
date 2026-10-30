package com.cquests.data;

import com.cquests.util.Sched;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Level;
import java.util.logging.Logger;

/** Loads and saves one YAML file per player under plugins/CQuests/players/. */
public final class PlayerStore {

    private final File dir;
    private final Logger log;
    private final Map<UUID, PlayerData> cache = new ConcurrentHashMap<>();

    public PlayerStore(File dataFolder, Logger log) {
        this.dir = new File(dataFolder, "players");
        this.log = log;
        //noinspection ResultOfMethodCallIgnored
        dir.mkdirs();
    }

    /** Safe to call from any thread; blocks on disk the first time a player is seen. */
    public PlayerData get(UUID uuid) {
        return cache.computeIfAbsent(uuid, this::load);
    }

    public PlayerData cached(UUID uuid) {
        return cache.get(uuid);
    }

    public void unload(UUID uuid) {
        PlayerData data = cache.remove(uuid);
        if (data != null && data.dirty()) {
            Sched.async(() -> write(data));
        }
    }

    public void saveDirtyAsync() {
        for (PlayerData data : cache.values()) {
            if (data.dirty()) {
                Sched.async(() -> write(data));
            }
        }
    }

    public void saveAllNow() {
        for (PlayerData data : cache.values()) {
            write(data);
        }
    }

    private PlayerData load(UUID uuid) {
        PlayerData data = new PlayerData(uuid);
        File file = new File(dir, uuid + ".yml");
        if (!file.exists()) {
            return data;
        }
        YamlConfiguration yaml = YamlConfiguration.loadConfiguration(file);
        ConfigurationSection active = yaml.getConfigurationSection("active");
        if (active != null) {
            for (String questId : active.getKeys(false)) {
                List<Integer> progress = active.getIntegerList(questId + ".progress");
                int[] values = new int[progress.size()];
                for (int i = 0; i < values.length; i++) {
                    values[i] = progress.get(i);
                }
                data.active.put(questId, new ActiveQuest(questId, values, active.getLong(questId + ".accepted")));
            }
        }
        data.completed.addAll(yaml.getStringList("completed"));
        data.met.addAll(yaml.getStringList("met"));
        ConfigurationSection side = yaml.getConfigurationSection("side-done");
        if (side != null) {
            for (String npcId : side.getKeys(false)) {
                data.sideDone.put(npcId, side.getInt(npcId));
            }
        }
        for (String line : yaml.getStringList("journey")) {
            JourneyEntry entry = JourneyEntry.parse(line);
            if (entry != null) {
                data.journey.add(entry);
            }
        }
        data.startedAt = yaml.getLong("started", 0);
        data.finaleReturn = yaml.getString("finale-return", null);
        data.lastDailyAt = yaml.getLong("daily.last", 0);
        data.dailiesDone = yaml.getInt("daily.done", 0);
        return data;
    }

    private void write(PlayerData data) {
        YamlConfiguration yaml = new YamlConfiguration();
        synchronized (data) {
            for (ActiveQuest quest : data.active.values()) {
                List<Integer> progress = new ArrayList<>();
                for (int p : quest.progress()) {
                    progress.add(p);
                }
                yaml.set("active." + quest.questId() + ".progress", progress);
                yaml.set("active." + quest.questId() + ".accepted", quest.acceptedAt());
            }
            yaml.set("completed", new ArrayList<>(data.completed));
            yaml.set("met", new ArrayList<>(data.met));
            data.sideDone.forEach((npcId, count) -> yaml.set("side-done." + npcId, count));
            yaml.set("journey", data.journey.stream().map(JourneyEntry::serialize).toList());
            yaml.set("started", data.startedAt);
            yaml.set("finale-return", data.finaleReturn);
            yaml.set("daily.last", data.lastDailyAt);
            yaml.set("daily.done", data.dailiesDone);
            data.clean();
        }
        // Serialise disk writes so two saves of the same player never race on its temp file.
        synchronized (dir) {
            writeFile(data, yaml);
        }
    }

    private void writeFile(PlayerData data, YamlConfiguration yaml) {
        try {
            File tmp = new File(dir, data.uuid() + ".yml.tmp");
            yaml.save(tmp);
            File target = new File(dir, data.uuid() + ".yml");
            if (!tmp.renameTo(target)) {
                yaml.save(target);
                //noinspection ResultOfMethodCallIgnored
                tmp.delete();
            }
        } catch (IOException e) {
            data.markDirty();
            log.log(Level.WARNING, "Could not save quest data for " + data.uuid(), e);
        }
    }
}
