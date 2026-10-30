package com.cquests;

import com.cquests.book.QuestBook;
import com.cquests.command.AdminCommand;
import com.cquests.command.QuestsCommand;
import com.cquests.data.PlayerStore;
import com.cquests.dialogue.DialogueManager;
import com.cquests.finale.Finale;
import com.cquests.listener.NpcListener;
import com.cquests.listener.ProgressListener;
import com.cquests.npc.NpcRegistry;
import com.cquests.npc.NpcTag;
import com.cquests.npc.SpawnManager;
import com.cquests.npc.VisibilityManager;
import com.cquests.quest.QuestManager;
import com.cquests.quest.QuestRegistry;
import com.cquests.util.Platform;
import com.cquests.util.Sched;
import io.papermc.paper.threadedregions.scheduler.ScheduledTask;
import org.bukkit.command.PluginCommand;
import org.bukkit.command.TabExecutor;
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
    private ScheduledTask autosave;

    @Override
    public void onEnable() {
        Sched.init(this);
        NpcTag.init(this);
        saveDefaultConfig();
        for (String resource : new String[]{"npcs.yml", "quests.yml", "generator.yml"}) {
            if (!new File(getDataFolder(), resource).exists()) {
                saveResource(resource, false);
            }
        }

        store = new PlayerStore(getDataFolder(), getLogger());
        questManager = new QuestManager(this);
        spawns = new SpawnManager(this);
        visibility = new VisibilityManager(this);
        dialogue = new DialogueManager(this);
        book = new QuestBook(this);
        finale = new Finale(this);

        loadData();
        Platform.init();
        finale.advancement().register();

        getServer().getPluginManager().registerEvents(new NpcListener(this), this);
        getServer().getPluginManager().registerEvents(new ProgressListener(this), this);
        register("quests", new QuestsCommand(this));
        register("cquests", new AdminCommand(this));

        spawns.load();
        spawns.start();
        autosave = Sched.asyncTimer(store::saveDirtyAsync, 120);
    }

    @Override
    public void onDisable() {
        if (autosave != null) {
            autosave.cancel();
        }
        if (store != null) {
            store.saveAllNow();
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
        settings = new Settings(getConfig());
        npcs.load(new File(getDataFolder(), "npcs.yml"), settings, getLogger());
        quests.load(new File(getDataFolder(), "quests.yml"), new File(getDataFolder(), "generator.yml"), settings, npcs, getLogger());
    }

    public void reload() {
        spawns.stop();
        store.saveDirtyAsync();
        loadData();
        Platform.init();
        spawns.load();
        spawns.start();
        visibility.refreshAll();
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

    public Finale finale() {
        return finale;
    }
}
