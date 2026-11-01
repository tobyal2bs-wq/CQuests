package com.cquests.listener;
import com.cquests.CQuestsPlugin;
import org.bukkit.event.inventory.*;
import org.junit.jupiter.api.Test;
import static org.mockito.Mockito.*;
class CraftGuardsTest {
    @Test void unsuccessfulCraftClickCannotAdvanceQuests(){
        CQuestsPlugin plugin=mock(CQuestsPlugin.class);CraftItemEvent event=mock(CraftItemEvent.class);
        when(event.getAction()).thenReturn(InventoryAction.NOTHING);
        new ProgressListener(plugin).onCraft(event);verifyNoInteractions(plugin);
    }
}
