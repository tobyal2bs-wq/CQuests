package com.cquests.data;

import com.cquests.util.Sched;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.InvalidConfigurationException;
import org.bukkit.configuration.file.YamlConfiguration;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Loads and saves one YAML file per player under plugins/CQuests/players/.
 * Every save is written to a temp file and moved into place, and the previous version is kept as
 * &lt;uuid&gt;.yml.bak, so a crash mid write or a broken file never loses a player's progress.
 */
public final class PlayerStore {

    private final File dir;
    private final Logger log;
    private final Map<UUID, PlayerData> cache = new ConcurrentHashMap<>();
    private final Map<UUID, Object> unloading = new ConcurrentHashMap<>();
    private final java.util.function.Consumer<Runnable> submit;

    public PlayerStore(File dataFolder, Logger log) {
        this(dataFolder, log, Sched::async);
    }

    PlayerStore(File dataFolder, Logger log, java.util.function.Consumer<Runnable> submit) {
        this.dir = new File(dataFolder, "players");
        this.log = log;
        this.submit = submit;
        //noinspection ResultOfMethodCallIgnored
        dir.mkdirs();
    }

    /** Safe to call from any thread; blocks on disk the first time a player is seen. */
    public PlayerData get(UUID uuid) {
        return cache.compute(uuid, (id, current) -> {
            // Reconnects reuse the latest ledger while the quit save is still queued.
            unloading.remove(id);
            return current == null ? load(id) : current;
        });
    }

    public File dir() {
        return dir;
    }

    public PlayerData cached(UUID uuid) {
        return cache.get(uuid);
    }

    public void unload(UUID uuid) {
        Object ticket = new Object();
        PlayerData data = cache.computeIfPresent(uuid, (id, current) -> {
            unloading.put(id, ticket);
            return current;
        });
        if (data == null) return;
        submit.accept(() -> {
            write(data);
            cache.computeIfPresent(uuid, (id, current) -> {
                if (current == data && unloading.get(id) == ticket) {
                    synchronized (dir) {
                        synchronized (data) {
                            if (!data.dirty() && data.writtenSeq >= data.saveSeq) {
                                unloading.remove(id, ticket);
                                data.retired = true;
                                return null;
                            }
                        }
                    }
                }
                return current;
            });
        });
    }

    public void saveDirtyAsync() {
        for (PlayerData data : cache.values()) {
            if (data.dirty()) {
                submit.accept(() -> write(data));
            }
        }
    }

    public void saveAllNow() {
        for (PlayerData data : cache.values()) {
            write(data);
        }
    }

    private PlayerData load(UUID uuid) {
        File file = new File(dir, uuid + ".yml");
        File bak = new File(dir, uuid + ".yml.bak");
        YamlConfiguration yaml = read(file);
        if (yaml == null && bak.exists()) {
            yaml = read(bak);
            if (yaml != null) {
                log.warning("Quest data for " + uuid + " was missing or broken; recovered it from the previous save.");
            }
        }
        if (yaml == null) {
            if (file.exists()) {
                log.severe("Quest data for " + uuid + " is broken and has no good previous save. Restore it with /cq restore.");
            }
            return new PlayerData(uuid);
        }
        return parse(uuid, yaml);
    }

    /** Reads a player file, or null if it is missing or not valid YAML. A broken file is kept aside for inspection. */
    private YamlConfiguration read(File file) {
        if (!file.exists()) {
            return null;
        }
        YamlConfiguration yaml = new YamlConfiguration();
        try {
            yaml.load(file);
            return yaml;
        } catch (IOException | InvalidConfigurationException e) {
            File broken = new File(dir, file.getName() + ".broken-" + System.currentTimeMillis());
            try {
                Files.copy(file.toPath(), broken.toPath());
            } catch (IOException ignored) {
                // nothing more we can do
            }
            log.log(Level.WARNING, "Could not read " + file.getName() + " (copied to " + broken.getName() + ")", e);
            return null;
        }
    }

    /** Turns a player's YAML into data. Also used to restore a player from a backup. */
    PlayerData parse(UUID uuid, YamlConfiguration yaml) {
        PlayerData data = new PlayerData(uuid);
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
        data.storyBookGiven = yaml.getBoolean("story-book", false);
        data.lastDailyAt = yaml.getLong("daily.last", 0);
        data.dailiesDone = yaml.getInt("daily.done", 0);
        data.trackerOn = yaml.contains("preferences.tracker") ? yaml.getBoolean("preferences.tracker") : null;
        data.directionsOn = yaml.contains("preferences.directions") ? yaml.getBoolean("preferences.directions") : null;
        String mode = yaml.getString("preferences.menu", "");
        data.menuMode = List.of("book", "menu", "chat").contains(mode) ? mode : null;
        data.skillXp = Math.max(0, yaml.getLong("skill.xp", 0));
        data.skillInitialized = yaml.getBoolean("skill.initialized", yaml.contains("skill.xp"));
        data.wheatHarvested = Math.max(0, yaml.getLong("skill.wheat", 0));
        data.hoeTier = Math.max(0, yaml.getInt("skill.hoe-tier", 0));
        data.sunflowersSpent = Math.max(0, Math.min(data.wheatHarvested / 750, yaml.getLong("discoveries.sunflowers-spent", 0)));
        for (String letter : yaml.getStringList("mail.read"))
            if (data.lettersRead.size() < 512 && letter.matches("[a-z0-9_-]{1,80}")) data.lettersRead.add(letter);
        var decisions = yaml.getConfigurationSection("npc-decisions");
        if (decisions != null) for (String quest : decisions.getKeys(false)) {
            String choice = decisions.getString(quest, "");
            if (data.decisions.size() < 256 && quest.matches("[a-z0-9_-]{1,80}")
                    && List.of("kind", "selfish").contains(choice) && data.completed.contains(quest))
                data.decisions.put(quest, choice);
        }
        return data;
    }

    /**
     * Saves right away: the snapshot is taken on the calling thread, the disk write happens async.
     * Used after rewards to minimize rollback; an abrupt process crash can still interrupt a queued save.
     */
    public void saveNow(PlayerData data) {
        Snapshot snapshot = snapshot(data);
        submit.accept(() -> writeIfNewer(data, snapshot));
    }

    private record Snapshot(YamlConfiguration yaml, long seq) {
    }

    private void write(PlayerData data) {
        writeIfNewer(data, snapshot(data));
    }

    private Snapshot snapshot(PlayerData data) {
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
            yaml.set("story-book", data.storyBookGiven);
            yaml.set("daily.last", data.lastDailyAt);
            yaml.set("daily.done", data.dailiesDone);
            yaml.set("preferences.tracker", data.trackerOn);
            yaml.set("preferences.directions", data.directionsOn);
            yaml.set("preferences.menu", data.menuMode);
            yaml.set("skill.xp", data.skillXp);
            yaml.set("skill.initialized", data.skillInitialized);
            yaml.set("skill.wheat", data.wheatHarvested);
            yaml.set("skill.hoe-tier", data.hoeTier);
            yaml.set("discoveries.sunflowers-spent", data.sunflowersSpent);
            yaml.set("mail.read", new ArrayList<>(data.lettersRead));
            data.decisions.forEach((quest, choice) -> yaml.set("npc-decisions." + quest, choice));
            data.clean();
            return new Snapshot(yaml, ++data.saveSeq);
        }
    }

    private void writeIfNewer(PlayerData data, Snapshot snapshot) {
        // Serialise disk writes, and never let an older snapshot overwrite a newer one.
        synchronized (dir) {
            if (data.retired || snapshot.seq() <= data.writtenSeq) {
                return;
            }
            writeFile(data, snapshot.yaml());
            data.writtenSeq = snapshot.seq();
        }
    }

    private void writeFile(PlayerData data, YamlConfiguration yaml) {
        try {
            File tmp = new File(dir, data.uuid() + ".yml.tmp");
            File target = new File(dir, data.uuid() + ".yml");
            Files.writeString(tmp.toPath(), yaml.saveToString(), StandardCharsets.UTF_8);
            if (target.exists()) {
                // Keep the last good version next to it in case the new one ever gets damaged.
                Files.copy(target.toPath(), new File(dir, data.uuid() + ".yml.bak").toPath(), StandardCopyOption.REPLACE_EXISTING);
            }
            try {
                Files.move(tmp.toPath(), target.toPath(), StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
            } catch (AtomicMoveNotSupportedException e) {
                Files.move(tmp.toPath(), target.toPath(), StandardCopyOption.REPLACE_EXISTING);
            }
        } catch (IOException e) {
            data.markDirty();
            log.log(Level.WARNING, "Could not save quest data for " + data.uuid(), e);
        }
    }

    /**
     * Replaces a player's saved data with a backup copy. If they are online the new data takes over
     * right away and the old copy in memory is retired, so a late save can't overwrite the restore.
     *
     * @return the restored data
     */
    public PlayerData restore(UUID uuid, String yamlText) throws InvalidConfigurationException, IOException {
        YamlConfiguration yaml = new YamlConfiguration();
        yaml.loadFromString(yamlText);
        PlayerData restored = parse(uuid, yaml);
        final IOException[] failure = new IOException[1];
        cache.compute(uuid, (id, old) -> {
            synchronized (dir) {
                try {
                    unloading.remove(id);
                    File target = new File(dir, uuid + ".yml");
                    if (target.exists()) {
                        Files.copy(target.toPath(), new File(dir, uuid + ".yml.before-restore").toPath(), StandardCopyOption.REPLACE_EXISTING);
                    }
                    Files.writeString(target.toPath(), yamlText, StandardCharsets.UTF_8);
                    if (old != null) old.retired = true;
                    return old == null ? null : restored;
                } catch (IOException e) { failure[0] = e; return old; }
            }
        });
        if (failure[0] != null) throw failure[0];
        return restored;
    }
}
