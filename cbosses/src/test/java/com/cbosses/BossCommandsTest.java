package com.cbosses;

import com.cbosses.fight.BossCommands;
import com.cbosses.fight.BossDef;
import org.bukkit.configuration.file.YamlConfiguration;
import org.junit.jupiter.api.Test;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import java.util.logging.Logger;

import static org.junit.jupiter.api.Assertions.*;

class BossCommandsTest {

    private static Map<String, BossDef> defs(YamlConfiguration yaml) {
        return BossDef.load(yaml, Logger.getLogger("test"));
    }

    private static YamlConfiguration bundled() throws Exception {
        try (var in = BossCommandsTest.class.getResourceAsStream("/bosses.yml")) {
            return YamlConfiguration.loadConfiguration(new InputStreamReader(in, StandardCharsets.UTF_8));
        }
    }

    @Test
    void groupAndOwnCommandsRunInOrder() throws Exception {
        YamlConfiguration bosses = bundled();
        Map<String, BossDef> all = defs(bosses);
        String big = all.values().stream().filter(d -> d.kind().equals("world")).findFirst().orElseThrow().id();
        String mini = all.values().stream().filter(BossDef::mini).findFirst().orElseThrow().id();
        bosses.set("bosses." + big + ".spawn-commands", List.of("say %bossname% woke"));
        bosses.set("bosses." + big + ".defeat-commands", List.of("/broadcast %boss% fell to %player%"));
        bosses.set("bosses." + mini + ".group-commands", false);
        YamlConfiguration config = new YamlConfiguration();
        config.set("rewards.commands.bosses.every-player", List.of("give %player% diamond 1"));
        config.set("rewards.commands.bosses.on-defeat", List.of("say a boss fell"));
        config.set("rewards.commands.minis.every-player", List.of("give %player% emerald 1"));
        BossCommands c = new BossCommands();
        c.load(bosses.getConfigurationSection("bosses"), config);
        all = defs(bosses);
        BossDef b = all.get(big), m = all.get(mini);
        assertEquals(List.of("give %player% diamond 1", "own"), c.forBoss(b, "every-player", List.of("own")));
        assertEquals(List.of("say a boss fell", "/broadcast %boss% fell to %player%"), c.forBoss(b, "on-defeat", null));
        assertEquals(List.of("say %bossname% woke"), c.forBoss(b, "on-spawn", null));
        // the mini opted out of the group lists but keeps its own
        assertEquals(List.of("own"), c.forBoss(m, "every-player", List.of("own")));
        assertEquals("broadcast x fell to Steve", BossCommands.fill("/broadcast %boss% fell to %player%", Map.of("boss", "x", "player", "Steve")));
    }

    @Test
    void groupsFollowTheKind() throws Exception {
        Map<String, BossDef> all = defs(bundled());
        for (BossDef d : all.values()) {
            List<String> g = BossCommands.groupsOf(d);
            if (d.mini()) assertEquals(List.of("minis"), g, d.id());
            else if (d.chapterBoss()) assertEquals(List.of("chapter"), g, d.id());
            else if (d.seasonal()) assertEquals(List.of("bosses", "seasonal"), g, d.id());
        }
    }

    @Test
    void bundledConfigHasEveryGroupList() throws Exception {
        try (var in = BossCommandsTest.class.getResourceAsStream("/config.yml")) {
            YamlConfiguration cfg = YamlConfiguration.loadConfiguration(new InputStreamReader(in, StandardCharsets.UTF_8));
            for (String g : List.of("bosses", "seasonal", "minis", "chapter"))
                for (String w : BossCommands.WHEN)
                    assertTrue(cfg.isList("rewards.commands." + g + "." + w), g + "." + w);
        }
    }
}
