package com.cquests.gui;

import org.bukkit.event.inventory.ClickType;
import org.bukkit.inventory.InventoryHolder;
import java.util.UUID;

public interface LockedMenu extends InventoryHolder {
    UUID viewer();
    void click(int slot, ClickType type);
}
