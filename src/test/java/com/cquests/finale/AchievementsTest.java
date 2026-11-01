package com.cquests.finale;

import com.cquests.CQuestsPlugin;
import com.cquests.quest.QuestRegistry;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.advancement.*;
import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class AchievementsTest {
    @Test void resetRevokesActualWayfarerAdvancement() {
        CQuestsPlugin plugin=mock(CQuestsPlugin.class);when(plugin.getName()).thenReturn("CQuests");
        QuestRegistry quests=mock(QuestRegistry.class);when(plugin.quests()).thenReturn(quests);when(quests.story()).thenReturn(List.of());
        Player player=mock(Player.class);Advancement advancement=mock(Advancement.class);
        AdvancementProgress progress=mock(AdvancementProgress.class);
        when(player.getAdvancementProgress(advancement)).thenReturn(progress);when(progress.getAwardedCriteria()).thenReturn(List.of("done"));
        try(var bukkit=mockStatic(Bukkit.class)){
            bukkit.when(()->Bukkit.getAdvancement(new NamespacedKey(plugin,"wayfarer_5"))).thenReturn(advancement);
            assertEquals(1,new Achievements(plugin).revokeAll(player));verify(progress).revokeCriteria("done");
        }
    }
}
