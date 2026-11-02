package com.cquests.quest;

import com.cquests.Settings;
import com.cquests.npc.NpcRegistry;
import org.bukkit.configuration.file.YamlConfiguration;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.io.*;
import java.nio.file.*;
import java.util.logging.Logger;
import static org.junit.jupiter.api.Assertions.*;

class StoryTwistsTest {
    @Test void additiveRevealsPreserveAllObjectivesRequirementsAndRewards(@TempDir File folder) throws Exception {
        Path resources=Path.of("src/main/resources");for(String file:new String[]{"quests.yml","generator.yml","twists.yml"})Files.copy(resources.resolve(file),folder.toPath().resolve(file));
        var settings=new Settings(YamlConfiguration.loadConfiguration(resources.resolve("config.yml").toFile()));var npcs=new NpcRegistry();var log=Logger.getLogger("twists-test");npcs.load(resources.resolve("npcs.yml").toFile(),settings,log);QuestRegistry.itemCheck=m->!m.isLegacy();
        var with=new QuestRegistry();with.load(new File(folder,"quests.yml"),new File(folder,"generator.yml"),settings,npcs,log);
        Files.writeString(folder.toPath().resolve("twists.yml"),"enabled: false\n");
        var plain=new QuestRegistry();plain.load(new File(folder,"quests.yml"),new File(folder,"generator.yml"),settings,npcs,log);
        assertEquals(plain.story().size(),with.story().size());
        for(var quest:plain.story()){
            var changed=with.get(quest.id());assertEquals(quest.objectives().stream().map(o->o.type()+":"+o.target().spec()+":"+o.amount()+":"+o.npc()).toList(),changed.objectives().stream().map(o->o.type()+":"+o.target().spec()+":"+o.amount()+":"+o.npc()).toList());assertEquals(quest.requires(),changed.requires());assertEquals(quest.reward(),changed.reward());assertEquals(quest.level(),changed.level());assertEquals(quest.order(),changed.order());
        }
        assertTrue(with.get("story_lucy").complete().size()>plain.get("story_lucy").complete().size());
        assertTrue(with.get("story_esme").complete().getFirst().contains("missing truth"));
        assertTrue(with.get("story_aldric").complete().getFirst().contains("hidden route"));
    }
}
