package com.cbosses;

import com.cbosses.api.CBossesAPI;
import com.cbosses.chapter.ChapterBosses;
import com.cbosses.command.BossCommand;
import com.cbosses.command.BossMenu;
import com.cbosses.fight.BossService;
import com.cbosses.fight.Fx;
import com.cbosses.hook.WorldGuardHook;
import com.cbosses.season.Seasons;
import com.cbosses.util.Sched;
import com.cbosses.util.Text;
import org.bukkit.command.CommandSender;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.plugin.java.JavaPlugin;

import java.io.File;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

/** CBosses: animated block-model bosses with weekly, seasonal and chapter fights. Paper and Folia. */
public final class CBossesPlugin extends JavaPlugin {
    private static CBossesPlugin instance;
    private BossService service;
    private ChapterBosses chapters;
    private Seasons seasons;
    private CBossesAPI api;
    private com.cbosses.finale.Finale finale;
    private com.cbosses.mini.MiniBosses minis;
    private com.cbosses.decor.Decor decor;
    private com.cbosses.friendly.FriendlyMossbacks friendlyMossbacks;
    private YamlConfiguration messages = new YamlConfiguration();

    public static CBossesPlugin instance() { return instance; }

    @Override
    public void onLoad() {
        // WorldGuard flags can only be registered before WorldGuard enables.
        if (getServer().getPluginManager().getPlugin("WorldGuard") != null) WorldGuardHook.registerFlags(getLogger());
    }

    @Override
    public void onEnable() {
        instance = this;
        saveDefaultConfig();
        getConfig().options().copyDefaults(true);
        saveConfig();
        if (!new File(getDataFolder(), "bosses.yml").exists()) saveResource("bosses.yml", false);
        if (!new File(getDataFolder(), "messages.yml").exists()) saveResource("messages.yml", false);
        loadMessages();
        Sched.init(this);
        Fx.init(this);
        WorldGuardHook.init(getServer().getPluginManager().getPlugin("WorldGuard") != null && getConfig().getBoolean("worldguard.enabled", true), getLogger());
        seasons = new Seasons(this);
        service = new BossService(this);
        chapters = new ChapterBosses(this);
        finale = new com.cbosses.finale.Finale(this);
        api = new CBossesAPI(this);
        getServer().getPluginManager().registerEvents(service, this);
        getServer().getPluginManager().registerEvents(chapters, this);
        getServer().getPluginManager().registerEvents(finale, this);
        minis = new com.cbosses.mini.MiniBosses(this);
        decor = new com.cbosses.decor.Decor(this);
        friendlyMossbacks = new com.cbosses.friendly.FriendlyMossbacks(this);
        getServer().getPluginManager().registerEvents(friendlyMossbacks, this);
        var mossbackCommand = getCommand("mossback");
        if (mossbackCommand != null) {
            mossbackCommand.setExecutor(friendlyMossbacks);
            mossbackCommand.setTabCompleter(friendlyMossbacks);
        }
        getServer().getPluginManager().registerEvents(minis, this);
        var miniMenu = new com.cbosses.mini.MiniMenu(this, minis);
        getServer().getPluginManager().registerEvents(miniMenu, this);
        BossMenu menu = new BossMenu(this);
        getServer().getPluginManager().registerEvents(menu, this);
        var settings = new com.cbosses.command.SettingsMenu(this);
        getServer().getPluginManager().registerEvents(settings, this);
        BossCommand command = new BossCommand(this, menu, settings, miniMenu);
        var cmd = getCommand("cbosses");
        if (cmd != null) { cmd.setExecutor(command); cmd.setTabCompleter(command); }
        service.start();
        minis.start();
        decor.start();
        friendlyMossbacks.start();
        if (getServer().getPluginManager().getPlugin("PlaceholderAPI") != null) {
            try { new com.cbosses.hook.Placeholders(this).register(); getLogger().info("PlaceholderAPI placeholders registered (%cbosses_...%)."); }
            catch (Throwable e) { getLogger().warning("Could not register placeholders: " + e); }
        }
        getLogger().info("CBosses " + getPluginMeta().getVersion() + " enabled with " + service.defs().size() + " bosses"
                + (WorldGuardHook.available() ? ", WorldGuard support on" : "")
                + (getServer().getPluginManager().getPlugin("CQuests") != null ? ", CQuests chapter bosses on" : "") + ".");
    }

    @Override
    public void onDisable() {
        if (friendlyMossbacks != null) friendlyMossbacks.stop();
        if (minis != null) minis.stop();
        if (decor != null) decor.stop();
        if (service != null) service.shutdown();
    }

    public void reloadAll() {
        reloadConfig();
        loadMessages();
        service.reload();
        service.start();
        minis.start();
        decor.start();
    }

    private void loadMessages() {
        File file = new File(getDataFolder(), "messages.yml");
        messages = YamlConfiguration.loadConfiguration(file);
        try (var in = getResource("messages.yml")) {
            if (in == null) return;
            YamlConfiguration jar = YamlConfiguration.loadConfiguration(new InputStreamReader(in, StandardCharsets.UTF_8));
            messages.setDefaults(jar);
            // lines added in an update are written into the server's file so they can be found and changed
            boolean added = false;
            YamlConfiguration own = YamlConfiguration.loadConfiguration(file);
            for (String key : jar.getKeys(true)) {
                if (jar.isConfigurationSection(key) || own.isSet(key)) continue;
                own.set(key, jar.get(key));
                added = true;
            }
            if (added) { own.save(file); messages = own; messages.setDefaults(jar); }
        } catch (Exception e) { getLogger().warning("Could not update messages.yml: " + e.getMessage()); }
    }

    public String msg(String key, String fallback) {
        String s = messages.getString(key);
        return s == null ? fallback : s;
    }

    public void send(CommandSender to, String miniMessage) {
        if (to == null) return;
        to.sendMessage(Text.mm(msg("prefix", "<dark_gray>[<gold>CBosses</gold>]</dark_gray> ") + miniMessage));
    }

    public BossService service() { return service; }
    public ChapterBosses chapters() { return chapters; }
    public com.cbosses.finale.Finale finale() { return finale; }
    public Seasons seasons() { return seasons; }
    public com.cbosses.mini.MiniBosses minis() { return minis; }
    public com.cbosses.decor.Decor decor() { return decor; }
    public CBossesAPI api() { return api; }

    /** config.yml is written through a temporary file with a .bak copy, so a crash mid-save never loses settings. */
    @Override
    public void saveConfig() {
        try { com.cbosses.util.SafeFiles.write(new java.io.File(getDataFolder(), "config.yml"), getConfig().saveToString()); }
        catch (java.io.IOException e) { getLogger().warning("Could not save config.yml: " + e.getMessage()); }
    }
}
