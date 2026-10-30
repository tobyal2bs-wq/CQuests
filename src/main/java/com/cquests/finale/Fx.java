package com.cquests.finale;

import com.cquests.util.Text;
import net.kyori.adventure.title.Title;
import org.bukkit.Color;
import org.bukkit.Location;
import org.bukkit.Particle;
import org.bukkit.Sound;
import org.bukkit.entity.Player;
import org.bukkit.plugin.Plugin;

import java.time.Duration;

/**
 * Small animation pieces used by the celebrations: a rising particle helix, an expanding ring, a
 * typed out title and short note melodies. Everything runs on the player's own scheduler, so it is
 * safe on Folia, and only that player gets the title and the sounds.
 */
final class Fx {

    /** Rising notes for a quest or chapter, as pitches on the note block scale (0.5 to 2.0). */
    static final float[] FANFARE = {0.749f, 0.943f, 1.122f, 1.498f};
    static final float[] CHAPTER = {0.594f, 0.749f, 0.891f, 1.189f, 0.891f, 1.189f, 1.498f};
    static final float[] ENDING = {0.5f, 0.63f, 0.749f, 1.0f, 0.749f, 1.0f, 1.26f, 1.498f, 2.0f};

    private Fx() {
    }

    /** Two coloured strands winding up around the player for about two seconds. */
    static void helix(Plugin plugin, Player player, Color a, Color b) {
        Particle.DustOptions first = new Particle.DustOptions(a, 1.2f);
        Particle.DustOptions second = new Particle.DustOptions(b, 1.2f);
        for (int step = 0; step < 20; step++) {
            int s = step;
            player.getScheduler().runDelayed(plugin, t -> {
                Location base = player.getLocation();
                for (int k = 0; k < 3; k++) {
                    double h = (s * 3 + k) * 0.045;
                    double angle = (s * 3 + k) * 0.42;
                    double radius = 1.1 - h * 0.25;
                    base.getWorld().spawnParticle(Particle.DUST, base.clone().add(Math.cos(angle) * radius, h, Math.sin(angle) * radius), 1, first);
                    base.getWorld().spawnParticle(Particle.DUST, base.clone().add(-Math.cos(angle) * radius, h, -Math.sin(angle) * radius), 1, second);
                }
                if (s == 19) {
                    base.getWorld().spawnParticle(Particle.END_ROD, base.clone().add(0, 2.8, 0), 30, 0.2, 0.2, 0.2, 0.12);
                }
            }, null, 1 + step);
        }
    }

    /** A flat ring of sparks that grows outward from the player's feet. */
    static void ring(Plugin plugin, Player player, Particle particle) {
        for (int step = 0; step < 8; step++) {
            int s = step;
            player.getScheduler().runDelayed(plugin, t -> {
                Location base = player.getLocation().add(0, 0.15, 0);
                double radius = 0.6 + s * 0.45;
                int points = 16 + s * 4;
                for (int i = 0; i < points; i++) {
                    double angle = Math.PI * 2 * i / points;
                    base.getWorld().spawnParticle(particle, base.clone().add(Math.cos(angle) * radius, 0, Math.sin(angle) * radius), 1, 0, 0, 0, 0);
                }
            }, null, 1 + step * 2L);
        }
    }

    /** Plays notes one after another, four ticks apart. */
    static void melody(Plugin plugin, Player player, Sound sound, float[] pitches) {
        for (int i = 0; i < pitches.length; i++) {
            float pitch = pitches[i];
            player.getScheduler().runDelayed(plugin, t -> player.playSound(player.getLocation(), sound, 0.9f, pitch), null, 1 + i * 4L);
        }
    }

    /**
     * Types the title out one letter at a time with a soft click per letter, then holds it.
     * {@code main} is plain text so it can be cut letter by letter; {@code style} wraps it.
     */
    static void typewriter(Plugin plugin, Player player, String style, String main, String subtitle, long holdMillis) {
        int length = main.length();
        for (int i = 1; i <= length; i++) {
            int shown = i;
            boolean last = i == length;
            player.getScheduler().runDelayed(plugin, t -> {
                String text = style.replace("<text>", Text.escape(main.substring(0, shown)));
                Title.Times times = Title.Times.times(Duration.ZERO, Duration.ofMillis(last ? holdMillis : 1000), Duration.ofMillis(last ? 800 : 0));
                player.showTitle(Title.title(Text.mm(text), last ? Text.mm(subtitle) : Text.mm(" "), times));
                if (main.charAt(shown - 1) != ' ') {
                    player.playSound(player.getLocation(), Sound.BLOCK_NOTE_BLOCK_HAT, 0.35f, 1.6f);
                }
            }, null, 1 + i * 2L);
        }
    }
}
