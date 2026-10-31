package com.cquests;

import com.cquests.book.QuestBook;
import com.cquests.command.AdminCommand;
import com.cquests.command.QuestsCommand;
import com.cquests.data.BackupManager;
import com.cquests.data.PlayerStore;
import com.cquests.dialogue.DialogueManager;
import com.cquests.finale.Finale;
import com.cquests.gui.MenuListener;
import com.cquests.gui.Tracker;
import com.cquests.gui.Directions;
import com.cquests.listener.NpcListener;
import com.cquests.listener.ProgressListener;
import com.cquests.listener.ShieldListener;
import com.cquests.npc.NpcRegistry;
import com.cquests.npc.NpcShield;
import com.cquests.npc.NpcTag;
import com.cquests.npc.SpawnManager;
import com.cquests.npc.VisibilityManager;
import com.cquests.quest.QuestManager;
import com.cquests.quest.QuestRegistry;
import com.cquests.util.Platform;
import com.cquests.util.Sched;
import com.cquests.util.Text;
import io.papermc.paper.threadedregions.scheduler.ScheduledTask;
import org.bukkit.command.CommandSender;
import org.bukkit.command.PluginCommand;
import org.bukkit.command.TabExecutor;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.plugin.java.JavaPlugin;

import java.io.File;

public final class CQuestsPlugin extends JavaPlugin {

    private Settings settings;
    private final NpcRegistry npcs = new NpcRegistry();
    private final QuestRegistry quests = new QuestRegistry();
    private PlayerStore store;
    private QuestManager questManager;
    private SpawnManager spawns;
    private VisibilityManager visibility;
    private DialogueManager dialogue;
    private QuestBook book;
    private Finale finale;
    private Tracker tracker;
    private Directions directions;
    private ScheduledTask displayTicker;
    private NpcShield shield;
    private ScheduledTask autosave;
    private BackupManager backups;

    @Override
    public void onEnable() {
        Sched.init(this);
        NpcTag.init(this);
        saveDefaultConfig();
        for (String resource : new String[]{"messages.yml", "npcs.yml", "quests.yml", "generator.yml"}) {
            if (!new File(getDataFolder(), resource).exists()) {
                saveResource(resource, false);
            }
        }

        ContentUpgrade.apply(this);
        store = new PlayerStore(getDataFolder(), getLogger());
        questManager = new QuestManager(this);
        spawns = new SpawnManager(this);
        visibility = new VisibilityManager(this);
        dialogue = new DialogueManager(this);
        book = new QuestBook(this);
        finale = new Finale(this);
        tracker = new Tracker(this);
        directions = new Directions(this);
        shield = new NpcShield(this);

        loadData();
        Platform.init();
        finale.achievements().register();

        getServer().getPluginManager().registerEvents(new NpcListener(this), this);
        getServer().getPluginManager().registerEvents(new ProgressListener(this), this);
        getServer().getPluginManager().registerEvents(new ShieldListener(this), this);
        getServer().getPluginManager().registerEvents(new MenuListener(), this);
        register("quests", new QuestsCommand(this));
        register("cquests", new AdminCommand(this));

        spawns.load();
        spawns.start();
        autosave = Sched.asyncTimer(store::saveDirtyAsync, 60);
        backups = new BackupManager(this);
        backups.start();
        displayTicker = Sched.globalTimer(t -> {
            for (var player : getServer().getOnlinePlayers()) Sched.entity(player, () -> {
                tracker.update(player); directions.update(player);
            });
        }, 20, 10);
    }

    @Override
    public void onDisable() {
        if (displayTicker != null) displayTicker.cancel();
        if (spawns != null) spawns.shutdown();
        if (autosave != null) {
            autosave.cancel();
        }
        if (backups != null) {
            backups.stop();
        }
        if (store != null) {
            store.saveAllNow();
            if (backups != null && settings.backupsEnabled) {
                backups.backup("shutdown");
            }
        }
        // NPC villagers are not persistent, so the server drops them on shutdown by itself.
    }

    private void register(String name, TabExecutor executor) {
        PluginCommand command = getCommand(name);
        if (command != null) {
            command.setExecutor(executor);
            command.setTabCompleter(executor);
        }
    }

    private void loadData() {
        reloadConfig();
        settings = new Settings(getConfig(), YamlConfiguration.loadConfiguration(new File(getDataFolder(), "messages.yml")));
        npcs.load(new File(getDataFolder(), "npcs.yml"), settings, getLogger());
        quests.load(new File(getDataFolder(), "quests.yml"), new File(getDataFolder(), "generator.yml"), settings, npcs, getLogger());
    }

    public void reload() {
        dialogue.invalidateAll();
        spawns.stop();
        store.saveDirtyAsync();
        loadData();
        Platform.init();
        spawns.load();
        spawns.start();
        backups.start();
        finale.achievements().register();
        visibility.refreshAll();
    }

    /** Sends a plugin message with the QUESTS prefix. Villager speech uses its own format instead. */
    public void send(CommandSender to, String miniMessage) {
        to.sendMessage(Text.mm(settings.prefix + miniMessage));
    }

    public Settings settings() {
        return settings;
    }

    public NpcRegistry npcs() {
        return npcs;
    }

    public QuestRegistry quests() {
        return quests;
    }

    public PlayerStore store() {
        return store;
    }

    public QuestManager questManager() {
        return questManager;
    }

    public SpawnManager spawns() {
        return spawns;
    }

    public VisibilityManager visibility() {
        return visibility;
    }

    public DialogueManager dialogue() {
        return dialogue;
    }

    public QuestBook book() {
        return book;
    }

    public BackupManager backups() {
        return backups;
    }

    public Tracker tracker() {
        return tracker;
    }

    public Directions directions() { return directions; }

    public Finale finale() {
        return finale;
    }

    public NpcShield shield() {
        return shield;
    }
}
