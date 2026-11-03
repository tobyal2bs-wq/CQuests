package com.cquests.farm;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class EconomyBridgeTest {
    @Test
    void readsBalancesTheWayServersShowThem() {
        assertEquals(5_000_000, EconomyBridge.parseAmount("$5,000,000.00"), 0.001);
        assertEquals(5_200_000, EconomyBridge.parseAmount("5.2M"), 0.001);
        assertEquals(12_000, EconomyBridge.parseAmount("12k"), 0.001);
        assertEquals(1234.5, EconomyBridge.parseAmount("\u00a7a1 234.5"), 0.001);
        assertTrue(Double.isNaN(EconomyBridge.parseAmount("%vault_eco_balance%")));
        assertTrue(Double.isNaN(EconomyBridge.parseAmount(null)));
    }
}
