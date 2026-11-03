package com.cquests.finale;

import com.cquests.CQuestsPlugin;
import com.cquests.data.JourneyEntry;
import com.cquests.data.PlayerData;
import com.cquests.model.NpcDef;
import com.cquests.model.Quest;
import com.cquests.npc.SpawnManager;
import com.cquests.util.Sched;
import com.cquests.util.Text;
import net.kyori.adventure.title.Title;
import org.bukkit.Bukkit;
import org.bukkit.Color;
import org.bukkit.FireworkEffect;
import org.bukkit.GameMode;
import org.bukkit.Location;
import org.bukkit.NamespacedKey;
import org.bukkit.Particle;
import org.bukkit.Sound;
import org.bukkit.World;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Firework;
import org.bukkit.entity.Player;
import org.bukkit.inventory.meta.FireworkMeta;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.potion.PotionEffect;
import org.bukkit.potion.PotionEffectType;
import org.bukkit.util.Vector;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Consumer;

/**
 * Celebrations for big quests and the ending: a camera tour (spectator mode) over the places the
 * player's story happened, a recap of their stats, "The End", fireworks and the custom advancement.
 */
public final class Finale {

    private record Scene(Location focus, String title, String subtitle) {
    }

    private final CQuestsPlugin plugin;
    private final NamespacedKey showKey;
    private final Achievements achievements;
    private final Set<UUID> playing = ConcurrentHashMap.newKeySet();

    public Finale(CQuestsPlugin plugin) {
        this.plugin = plugin;
        this.showKey = new NamespacedKey(plugin, "show");
        this.achievements = new Achievements(plugin);
    }

    public Achievements achievements() {
        return achievements;
    }

    /** Our display fireworks are tagged so the damage listener can make them harmless. */
    public boolean isShowFirework(Entity entity) {
        return entity instanceof Firework && entity.getPersistentDataContainer().has(showKey, PersistentDataType.BYTE);
    }

    public boolean isPlaying(Player player) {
        return playing.contains(player.getUniqueId());
    }

    // ------------------------------------------------------------------ big quest celebration

    public void celebrate(Player player, Quest quest) {
        if (plugin.settings().celebrateBigQuests) {
            celebrate(player, "<gold><bold>Quest Complete</bold></gold>", "<yellow>" + Text.escape(quest.name()));
        }
    }

    private void celebrate(Player player, String main, String sub) {
        player.showTitle(title(main, sub, 3000));
        player.playSound(player.getLocation(), Sound.UI_TOAST_CHALLENGE_COMPLETE, 1f, 1f);
        Fx.helix(plugin, player, Color.fromRGB(0xFFC94A), Color.fromRGB(0x8FD3FF));
        Fx.melody(plugin, player, Sound.BLOCK_NOTE_BLOCK_BELL, Fx.FANFARE);
        Sched.entityLater(player, 20, () -> player.getWorld().spawnParticle(Particle.TOTEM_OF_UNDYING,
                player.getLocation().add(0, 1.5, 0), 60, 0.5, 0.8, 0.5, 0.3));
        for (int i = 0; i < 3; i++) {
            int n = i;
            Sched.entityLater(player, 1 + i * 12L, () -> firework(player.getLocation().add(Math.cos(n * 2.1) * 2.5, 1, Math.sin(n * 2.1) * 2.5), n));
        }
    }

    /** End of a chapter: celebration, then the next chapter's title card. */
    public void chapterComplete(Player player, Quest last, Quest next) {
        if (!plugin.settings().celebrateBigQuests) {
            return;
        }
        String name = plugin.quests().chapterName(last.chapter());
        // 1. The chapter title types itself out over a golden helix and a little fanfare.
        Fx.typewriter(plugin, player, "<gradient:#ffd36b:#ff9a3c><bold><text></bold></gradient>", "CHAPTER " + last.chapter() + " COMPLETE",
                "<white>" + Text.escape(name.isEmpty() ? last.name() : name), 3500);
        Fx.helix(plugin, player, Color.fromRGB(0xFFD36B), Color.fromRGB(0xFFFFFF));
        Fx.melody(plugin, player, Sound.BLOCK_NOTE_BLOCK_CHIME, Fx.CHAPTER);
        // 2. Fireworks in a circle and a ring of sparks.
        Sched.entityLater(player, 44, () -> {
            player.playSound(player.getLocation(), Sound.UI_TOAST_CHALLENGE_COMPLETE, 1f, 1f);
            Fx.ring(plugin, player, Particle.END_ROD);
            for (int i = 0; i < 5; i++) {
                double angle = i * Math.PI * 2 / 5;
                firework(player.getLocation().add(Math.cos(angle) * 3, 1, Math.sin(angle) * 3), i);
            }
        });
        if (next != null) {
            // 3. A short fade to dark, then the next chapter card with a bell.
            String nextName = plugin.quests().chapterName(next.chapter());
            Sched.entityLater(player, 120, () -> {
                player.addPotionEffect(new PotionEffect(PotionEffectType.DARKNESS, 50, 0, false, false, false));
                player.playSound(player.getLocation(), Sound.BLOCK_BEACON_POWER_SELECT, 0.8f, 0.6f);
            });
            Sched.entityLater(player, 150, () -> {
                Fx.typewriter(plugin, player, "<white><bold><text></bold></white>", "CHAPTER " + next.chapter(),
                        "<gradient:#8fd3ff:#c9a7ff>" + Text.escape(nextName) + "</gradient>", 4000);
                player.playSound(player.getLocation(), Sound.BLOCK_BELL_USE, 1f, 0.7f);
                player.getWorld().spawnParticle(Particle.ENCHANT, player.getLocation().add(0, 1.2, 0), 120, 0.8, 1, 0.8, 1);
            });
        }
    }

    // ------------------------------------------------------------------ the ending

    public void play(Player player) {
        play(player, false);
    }

    /** @param preview admin preview: no advancement, no broadcast */
    public void play(Player player, boolean preview) {
        if (!plugin.settings().finaleEnabled && !preview) {
            award(player);
            return;
        }
        if (!playing.add(player.getUniqueId())) {
            return;
        }
        PlayerData data = plugin.questManager().data(player);
        Location origin = player.getLocation();
        GameMode mode = player.getGameMode() == GameMode.SPECTATOR ? GameMode.SURVIVAL : player.getGameMode();
        data.setFinaleReturn(serialize(origin, mode));

        List<Scene> scenes = scenes(data, origin);
        long days = Math.max(1, (System.currentTimeMillis() - (data.startedAt() == 0 ? System.currentTimeMillis() : data.startedAt())) / 86_400_000L);
        int sceneTicks = plugin.settings().finaleSceneTicks;

        List<Step> steps = new ArrayList<>();
        steps.add(new Step(10, p -> {
            p.setGameMode(GameMode.SPECTATOR);
            p.showTitle(title("<gold><bold>Your Journey</bold></gold>", "<gray>" + days + (days == 1 ? " day" : " days") + " on the road", 3500));
            p.playSound(p.getLocation(), Sound.BLOCK_BEACON_ACTIVATE, 1f, 0.8f);
        }));
        steps.add(new Step(80, p -> { }));
        for (int i = 0; i < scenes.size(); i++) {
            Scene scene = scenes.get(i);
            int index = i;
            steps.add(new Step(sceneTicks, p -> {
                p.teleportAsync(camera(scene.focus(), index));
                p.showTitle(title("<yellow>" + scene.title(), "<gray>" + scene.subtitle(), sceneTicks * 50L - 600));
                p.playSound(p.getLocation(), Sound.BLOCK_NOTE_BLOCK_CHIME, 0.8f, 0.7f + 0.05f * index);
            }));
        }
        steps.add(new Step(90, p -> {
            p.teleportAsync(overview(origin));
            p.showTitle(title("<green>" + data.completedCount() + " story quests",
                    "<gray>" + String.format(Locale.ROOT, "%,d", data.totalSideDone()) + " side jobs · " + data.dailiesDone() + " dailies", 4000));
            p.playSound(p.getLocation(), Sound.BLOCK_NOTE_BLOCK_BELL, 1f, 1f);
        }));
        steps.add(new Step(120, p -> {
            Fx.typewriter(plugin, p, "<gradient:#ffd36b:#ff9a3c><bold><text></bold></gradient>", "The End",
                    "<white>Thank you for playing, " + Text.escape(p.getName()), 5000);
            Fx.melody(plugin, p, Sound.BLOCK_NOTE_BLOCK_BELL, Fx.ENDING);
            p.playSound(p.getLocation(), Sound.UI_TOAST_CHALLENGE_COMPLETE, 1f, 1f);
            for (int i = 0; i < 6; i++) {
                double angle = i * Math.PI / 3;
                firework(origin.clone().add(Math.cos(angle) * 4, 2, Math.sin(angle) * 4), i);
            }
        }));
        steps.add(new Step(1, p -> {
            restore(p, data, preview);
        }));
        run(player, steps, 0);
    }

    /** Puts a player back if they logged out mid-cinematic. Call on join. */
    public void restoreIfNeeded(Player player) {
        PlayerData data = plugin.questManager().data(player);
        if (data.finaleReturn() != null && !playing.contains(player.getUniqueId())) {
            restore(player, data, false);
        }
    }

    private record Step(long ticksAfter, Consumer<Player> action) {
    }

    private void run(Player player, List<Step> steps, int index) {
        if (index >= steps.size()) {
            playing.remove(player.getUniqueId());
            return;
        }
        Step step = steps.get(index);
        step.action().accept(player);
        player.getScheduler().runDelayed(plugin, t -> run(player, steps, index + 1),
                () -> playing.remove(player.getUniqueId()), Math.max(1, step.ticksAfter()));
    }

    private void restore(Player player, PlayerData data, boolean preview) {
        String saved = data.finaleReturn();
        data.setFinaleReturn(null);
        playing.remove(player.getUniqueId());
        Location back = null;
        GameMode mode = GameMode.SURVIVAL;
        if (saved != null) {
            String[] p = saved.split(";");
            World world = p.length >= 7 ? Bukkit.getWorld(p[0]) : null;
            if (world != null) {
                back = new Location(world, Double.parseDouble(p[1]), Double.parseDouble(p[2]), Double.parseDouble(p[3]),
                        Float.parseFloat(p[4]), Float.parseFloat(p[5]));
                try {
                    mode = GameMode.valueOf(p[6]);
                } catch (IllegalArgumentException ignored) {
                    // keep survival
                }
            }
        }
        GameMode finalMode = mode;
        Runnable finish = () -> {
            player.setGameMode(finalMode);
            if (!preview) {
                award(player);
            }
        };
        if (back != null) {
            player.teleportAsync(back).thenRun(() -> Sched.entity(player, finish));
        } else {
            finish.run();
        }
    }

    private void award(Player player) {
        achievements.grantJourney(player);
        StoryBook.give(plugin, player);
        Bukkit.broadcast(Text.mm(plugin.settings().msg("journey-finished",
                "<gold>★ <white><player></white> finished the journey and freed the Hollow King!")
                .replace("<player>", Text.escape(player.getName()))));
        if (plugin.discord() != null) plugin.discord().journeyFinished(player);
    }

    // ------------------------------------------------------------------ scenes & camera

    /** Up to finale.max-scenes moments from the player's story, spread evenly, always the first and last. */
    private List<Scene> scenes(PlayerData data, Location fallback) {
        List<JourneyEntry> journey = new ArrayList<>(data.journey());
        if (journey.isEmpty()) {
            // Preview for someone who hasn't played: walk past the story villagers instead.
            for (Quest quest : plugin.quests().story()) {
                SpawnManager.Point point = plugin.spawns().points().get(quest.giver());
                if (point != null) {
                    journey.add(new JourneyEntry(quest.id(), 0, point.world(), point.x(), point.y(), point.z()));
                }
            }
        }
        int max = plugin.settings().finaleMaxScenes;
        List<JourneyEntry> picked = new ArrayList<>();
        if (journey.size() <= max) {
            picked.addAll(journey);
        } else {
            for (int i = 0; i < max; i++) {
                picked.add(journey.get((int) Math.round(i * (journey.size() - 1) / (double) (max - 1))));
            }
        }
        long start = data.startedAt() == 0 ? (picked.isEmpty() ? 0 : picked.get(0).time()) : data.startedAt();
        List<Scene> scenes = new ArrayList<>();
        for (JourneyEntry entry : picked) {
            World world = Bukkit.getWorld(entry.world());
            Location focus = world == null ? fallback : new Location(world, entry.x(), entry.y(), entry.z());
            Quest quest = plugin.quests().get(entry.questId());
            String name = quest == null ? entry.questId() : Text.escape(quest.name());
            int chapter = quest == null ? 0 : quest.chapter();
            NpcDef npc = quest == null ? null : plugin.npcs().get(quest.giver());
            StringBuilder subtitle = new StringBuilder("Chapter " + chapter);
            if (npc != null) {
                subtitle.append(" · ").append(Text.escape(npc.name()));
            }
            if (entry.time() > 0 && start > 0) {
                subtitle.append(" · Day ").append(1 + (entry.time() - start) / 86_400_000L);
            }
            scenes.add(new Scene(focus, name, subtitle.toString()));
        }
        return scenes;
    }

    /** A spot a few blocks up and away, looking at the focus; the angle changes every scene. */
    private static Location camera(Location focus, int index) {
        double angle = Math.toRadians(index * 67.0);
        Location camera = focus.clone().add(Math.cos(angle) * 7, 4, Math.sin(angle) * 7);
        Vector look = focus.clone().add(0, 1.5, 0).toVector().subtract(camera.toVector());
        camera.setDirection(look);
        return camera;
    }

    private static Location overview(Location origin) {
        Location camera = origin.clone().add(0, 25, -12);
        camera.setDirection(origin.toVector().subtract(camera.toVector()));
        return camera;
    }

    private void firework(Location at, int variant) {
        Color[][] palettes = {
                {Color.ORANGE, Color.YELLOW}, {Color.AQUA, Color.WHITE}, {Color.LIME, Color.GREEN},
                {Color.FUCHSIA, Color.PURPLE}, {Color.RED, Color.ORANGE}, {Color.BLUE, Color.AQUA}};
        Color[] palette = palettes[Math.floorMod(variant, palettes.length)];
        Consumer<Firework> setup = fw -> {
            fw.getPersistentDataContainer().set(showKey, PersistentDataType.BYTE, (byte) 1);
            FireworkMeta meta = fw.getFireworkMeta();
            meta.addEffect(FireworkEffect.builder()
                    .with(variant % 2 == 0 ? FireworkEffect.Type.BALL_LARGE : FireworkEffect.Type.STAR)
                    .withColor(palette).withFade(Color.WHITE).trail(true).flicker(true).build());
            meta.setPower(1);
            fw.setFireworkMeta(meta);
        };
        Sched.at(at, () -> at.getWorld().spawn(at, Firework.class, setup));
    }

    private static String serialize(Location loc, GameMode mode) {
        return loc.getWorld().getName() + ";" + loc.getX() + ";" + loc.getY() + ";" + loc.getZ() + ";"
                + loc.getYaw() + ";" + loc.getPitch() + ";" + mode.name();
    }

    private static Title title(String main, String sub, long stayMillis) {
        return Title.title(Text.mm(main), Text.mm(sub),
                Title.Times.times(Duration.ofMillis(500), Duration.ofMillis(Math.max(1000, stayMillis)), Duration.ofMillis(700)));
    }
}
