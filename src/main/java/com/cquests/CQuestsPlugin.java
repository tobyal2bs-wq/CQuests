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
import com.cquests.dialogue.SpeechController;
import com.cquests.progression.Progression;
import com.cquests.farm.FarmService;
import com.cquests.farm.FarmCommand;
import com.cquests.farm.FarmListener;
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
    private SpeechController speech;
    private com.cquests.npc.NpcNameplates nameplates;
    private Progression progression;
    private FarmService farm;
    private FarmCommand farmCommand;
    private ScheduledTask farmSave;
    private NpcShield shield;
    private ScheduledTask autosave;
    private BackupManager backups;
    private com.cquests.merchant.MerchantService merchants;

    @Override
    public void onEnable() {
        Sched.init(this);
        NpcTag.init(this);
        saveDefaultConfig();
        // Only migrate the previous bundled reward command; custom command strings are preserved.
        if ("eco give %player% %amount%".equals(getConfig().getString("money-command"))) {
            try {
                var configFile=new File(getDataFolder(),"config.yml").toPath();
                var backup=configFile.resolveSibling("config.yml.before-1.2.0");
                if(!java.nio.file.Files.exists(backup))java.nio.file.Files.copy(configFile,backup);
                getConfig().set("money-command","economy give %player% %amount%");saveConfig();
            } catch(java.io.IOException e){getLogger().warning("Reward command migration deferred: "+e.getMessage());}
        }
        for (String resource : new String[]{"messages.yml", "npcs.yml", "quests.yml", "generator.yml", "farming.yml", "merchants.yml", "twists.yml"}) {
            if (!new File(getDataFolder(), resource).exists()) {
                saveResource(resource, false);
            }
        }

        ContentUpgrade.apply(this);
        store = new PlayerStore(getDataFolder(), getLogger());
        questManager = new QuestManager(this);
        nameplates = new com.cquests.npc.NpcNameplates(this);
        spawns = new SpawnManager(this);
        visibility = new VisibilityManager(this);
        dialogue = new DialogueManager(this);
        book = new QuestBook(this);
        finale = new Finale(this);
        tracker = new Tracker(this);
        directions = new Directions(this);
        speech = new SpeechController(this);
        progression = new Progression(this);
        farm = new FarmService(this);
        farmCommand = new FarmCommand(this);
        shield = new NpcShield(this);
        merchants = new com.cquests.merchant.MerchantService(this);

        loadData();
        Platform.init();
        finale.achievements().register();

        getServer().getPluginManager().registerEvents(new NpcListener(this), this);
        getServer().getPluginManager().registerEvents(new ProgressListener(this), this);
        getServer().getPluginManager().registerEvents(new ShieldListener(this), this);
        getServer().getPluginManager().registerEvents(new MenuListener(this), this);
        getServer().getPluginManager().registerEvents(speech, this);
        getServer().getPluginManager().registerEvents(new FarmListener(this), this);
        getServer().getPluginManager().registerEvents(new com.cquests.merchant.MerchantListener(this), this);
        register("quests", new QuestsCommand(this));
        register("cquests", new AdminCommand(this));

        spawns.load();
        spawns.start();
        merchants.start();
        autosave = Sched.asyncTimer(store::saveDirtyAsync, 60);
        backups = new BackupManager(this);
        backups.start();
        farmSave = Sched.asyncTimer(farm::savePending, 5);
        if (getServer().getPluginManager().isPluginEnabled("PlaceholderAPI")) new com.cquests.progression.SkillPlaceholders(this).register();
        displayTicker = Sched.globalTimer(t -> {
            for (var player : getServer().getOnlinePlayers()) Sched.entity(player, () -> {
                tracker.update(player); farm.update(player);
                if (!farm.inFarm(player) && !speech.busy(player)) directions.update(player);
            });
        }, 20, 10);
    }

    @Override
    public void onDisable() {
        if(merchants!=null)merchants.shutdown();
        if (farmSave != null) farmSave.cancel();
        if (farm != null) farm.shutdown();
        if (speech != null) speech.stopAll();
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
        speech.stopAll();
        dialogue.invalidateAll();
        spawns.stop();
        store.saveDirtyAsync();
        loadData();
        Platform.init();
        spawns.load();
        progression.reload(); farm.reload();
        merchants.reload();
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
    public SpeechController speech() { return speech; }
    public com.cquests.npc.NpcNameplates nameplates(){return nameplates;}
    public Progression progression() { return progression; }
    public FarmService farm() { return farm; }
    public FarmCommand farmCommand() { return farmCommand; }
    public com.cquests.merchant.MerchantService merchants(){return merchants;}

    public Finale finale() {
        return finale;
    }

    public NpcShield shield() {
        return shield;
    }
}
