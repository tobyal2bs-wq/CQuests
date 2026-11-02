package com.cquests.progression;

import com.cquests.CQuestsPlugin;
import com.cquests.data.PlayerData;
import com.cquests.util.Text;
import org.bukkit.Sound;
import org.bukkit.entity.Player;
import org.bukkit.configuration.file.YamlConfiguration;
import java.io.File;

public final class Progression {
    private final CQuestsPlugin plugin;
    private LevelCurve curve;
    private boolean gates;
    public Progression(CQuestsPlugin plugin) { this.plugin = plugin; reload(); }
    public void reload() {
        var cfg = YamlConfiguration.loadConfiguration(new File(plugin.getDataFolder(), "farming.yml"));
        int configured=cfg.getInt("levels.maximum",500);
        int max = Math.max(2, Math.min(1000,configured));
        long xp = Math.max(max, Math.round(cfg.getDouble("levels.target-active-hours", 360)
                * 3600 * cfg.getDouble("levels.reference-xp-per-second", 30)));
        curve = new LevelCurve(max, xp, Math.max(1, cfg.getDouble("levels.curve-exponent", 2.2)));
        gates = cfg.getBoolean("levels.quest-gates", true);
    }
    public LevelCurve curve() { return curve; }
    /** Existing journeys retain the level needed by their completed and active story steps. */
    public void initialize(Player player) {
        PlayerData data=plugin.questManager().data(player);
        if(data.skillInitialized())return;
        int level=1;
        for(var quest:plugin.quests().story())if(data.isCompleted(quest.id())||data.isActive(quest.id()))level=Math.max(level,quest.level());
        data.initializeSkill(curve.threshold(Math.min(level,curve.maxLevel())));
        plugin.store().saveNow(data);
    }
    public int level(PlayerData data) { return curve.level(data.skillXp()); }
    public boolean canTake(PlayerData data, int required) { return !gates || level(data) >= Math.max(1, required); }
    public void award(Player player, long amount, boolean showHud) {
        PlayerData data = plugin.questManager().data(player);
        int before = level(data);
        data.addSkillXp(amount);
        int after = level(data);
        if (showHud) hud(player, amount);
        if (after > before) {
            plugin.send(player, "<gold><bold>WAYFARER LEVEL " + after + "</bold> <white>Your next chapter is closer.");
            player.sendMessage(Text.mm("<gray>Next level: <aqua>" + Text.formatMoney(curve.remaining(data.skillXp())) + " skill XP</aqua>."));
            player.playSound(player.getLocation(), Sound.ENTITY_PLAYER_LEVELUP, .6f, 1.25f);
            plugin.finale().achievements().sync(player);
        }
    }
    public void hud(Player player, long gain) {
        PlayerData data = plugin.questManager().data(player);
        int filled = (int) Math.round(curve.progress(data.skillXp()) * 12);
        player.sendActionBar(Text.mm("<gold>+" + gain + " skill XP</gold> <dark_gray>│</dark_gray> <aqua>"
                + "▰".repeat(filled) + "<gray>" + "▱".repeat(12 - filled) + "</gray> <white>"
                + Math.round(curve.progress(data.skillXp()) * 100) + "%</white> <dark_gray>│</dark_gray> <yellow>Lv " + level(data)));
    }
}
