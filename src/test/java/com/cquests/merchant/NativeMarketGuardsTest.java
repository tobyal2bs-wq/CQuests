package com.cquests.merchant;

import com.cquests.CQuestsPlugin;
import org.bukkit.NamespacedKey;
import org.bukkit.entity.Player;
import org.bukkit.event.inventory.*;
import org.bukkit.inventory.*;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.persistence.*;
import org.junit.jupiter.api.Test;
import java.util.UUID;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class NativeMarketGuardsTest {
    private NativeMarket market(){var plugin=mock(CQuestsPlugin.class);when(plugin.getName()).thenReturn("CQuests");return new NativeMarket(plugin);}
    private ItemStack ghost(){var item=mock(ItemStack.class);var meta=mock(ItemMeta.class);var data=mock(PersistentDataContainer.class);when(item.hasItemMeta()).thenReturn(true);when(item.getItemMeta()).thenReturn(meta);when(meta.getPersistentDataContainer()).thenReturn(data);when(data.has(any(NamespacedKey.class),eq(PersistentDataType.STRING))).thenReturn(true);return item;}
    @Test void previewCannotBeMovedByAnotherInventoryPlugin(){var event=mock(InventoryMoveItemEvent.class);var preview=ghost();when(event.getItem()).thenReturn(preview);market().move(event);verify(event).setCancelled(true);}
    @Test void numberKeyCannotMovePreviewIntoAnUnrelatedContainer(){
        var player=mock(Player.class);var inventory=mock(PlayerInventory.class);when(player.getUniqueId()).thenReturn(UUID.randomUUID());when(player.getInventory()).thenReturn(inventory);var preview=ghost();when(inventory.getItem(3)).thenReturn(preview);
        var view=mock(InventoryView.class);when(view.getPlayer()).thenReturn(player);var event=mock(InventoryClickEvent.class);when(event.getView()).thenReturn(view);when(event.getWhoClicked()).thenReturn(player);when(event.getHotbarButton()).thenReturn(3);
        market().click(event);verify(event).setCancelled(true);
    }
    @Test void ordinaryItemsAreNotMarkedAsPreviews(){var market=market();assertFalse(market.ghost(null));var item=mock(ItemStack.class);assertFalse(market.ghost(item));}
}
