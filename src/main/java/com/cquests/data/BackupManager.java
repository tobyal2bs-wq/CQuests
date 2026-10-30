package com.cquests.data;

import com.cquests.CQuestsPlugin;
import com.cquests.util.Sched;
import io.papermc.paper.threadedregions.scheduler.ScheduledTask;

import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.Date;
import java.util.Enumeration;
import java.util.List;
import java.util.Locale;
import java.util.UUID;
import java.util.logging.Level;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import java.util.zip.ZipOutputStream;

/**
 * Zips every player's quest file (plus spawns.yml) into plugins/CQuests/backups/ on a timer and on
 * shutdown, keeping the newest few. Any single player, or everyone, can be put back with /cq restore.
 */
public final class BackupManager {

    private static final String PREFIX = "backup-";

    private final CQuestsPlugin plugin;
    private final File folder;
    private ScheduledTask timer;

    public BackupManager(CQuestsPlugin plugin) {
        this.plugin = plugin;
        this.folder = new File(plugin.getDataFolder(), "backups");
    }

    public void start() {
        stop();
        if (!plugin.settings().backupsEnabled) {
            return;
        }
        long seconds = Math.max(1, plugin.settings().backupEveryHours) * 3600L;
        timer = Sched.asyncTimer(() -> backup("auto"), seconds);
    }

    public void stop() {
        if (timer != null) {
            timer.cancel();
            timer = null;
        }
    }

    /** Saves everyone in memory, then writes a new backup zip. Blocks; call it off the main thread. */
    public synchronized String backup(String reason) {
        plugin.store().saveAllNow();
        //noinspection ResultOfMethodCallIgnored
        folder.mkdirs();
        String name = PREFIX + new SimpleDateFormat("yyyy-MM-dd_HH-mm-ss", Locale.ROOT).format(new Date()) + "-" + reason + ".zip";
        File zip = new File(folder, name);
        File players = plugin.store().dir();
        int count = 0;
        try (OutputStream out = Files.newOutputStream(zip.toPath()); ZipOutputStream zos = new ZipOutputStream(out)) {
            synchronized (players) {
                File[] files = players.listFiles((dir, file) -> file.endsWith(".yml"));
                if (files != null) {
                    for (File file : files) {
                        zos.putNextEntry(new ZipEntry("players/" + file.getName()));
                        Files.copy(file.toPath(), zos);
                        zos.closeEntry();
                        count++;
                    }
                }
            }
            File spawns = new File(plugin.getDataFolder(), "spawns.yml");
            if (spawns.exists()) {
                zos.putNextEntry(new ZipEntry("spawns.yml"));
                Files.copy(spawns.toPath(), zos);
                zos.closeEntry();
            }
        } catch (IOException e) {
            plugin.getLogger().log(Level.WARNING, "Backup failed", e);
            //noinspection ResultOfMethodCallIgnored
            zip.delete();
            return null;
        }
        prune();
        plugin.getLogger().info("Backed up " + count + " players to backups/" + name);
        return name;
    }

    private void prune() {
        List<File> all = files();
        int keep = Math.max(1, plugin.settings().backupKeep);
        for (int i = keep; i < all.size(); i++) {
            //noinspection ResultOfMethodCallIgnored
            all.get(i).delete();
        }
    }

    /** Backup files, newest first. */
    public List<File> files() {
        File[] files = folder.listFiles((dir, name) -> name.startsWith(PREFIX) && name.endsWith(".zip"));
        if (files == null) {
            return List.of();
        }
        List<File> list = new ArrayList<>(Arrays.asList(files));
        list.sort(Comparator.comparing(File::getName).reversed());
        return list;
    }

    /** Finds a backup by its file name, or "latest". */
    public File find(String name) {
        List<File> all = files();
        if (name.equalsIgnoreCase("latest")) {
            return all.isEmpty() ? null : all.get(0);
        }
        for (File file : all) {
            if (file.getName().equalsIgnoreCase(name) || file.getName().equalsIgnoreCase(name + ".zip")) {
                return file;
            }
        }
        return null;
    }

    /**
     * Restores one player (or everyone when {@code uuid} is null) from a backup.
     *
     * @return the players restored
     */
    public List<UUID> restore(File backup, UUID uuid) throws IOException {
        List<UUID> restored = new ArrayList<>();
        try (ZipFile zip = new ZipFile(backup)) {
            Enumeration<? extends ZipEntry> entries = zip.entries();
            while (entries.hasMoreElements()) {
                ZipEntry entry = entries.nextElement();
                String name = entry.getName();
                if (!name.startsWith("players/") || !name.endsWith(".yml")) {
                    continue;
                }
                UUID id;
                try {
                    id = UUID.fromString(name.substring("players/".length(), name.length() - ".yml".length()));
                } catch (IllegalArgumentException e) {
                    continue;
                }
                if (uuid != null && !uuid.equals(id)) {
                    continue;
                }
                String text = new String(zip.getInputStream(entry).readAllBytes(), StandardCharsets.UTF_8);
                try {
                    plugin.store().restore(id, text);
                    restored.add(id);
                } catch (org.bukkit.configuration.InvalidConfigurationException e) {
                    plugin.getLogger().warning("Skipped " + name + " in " + backup.getName() + ": not valid YAML");
                }
            }
        }
        return restored;
    }
}
