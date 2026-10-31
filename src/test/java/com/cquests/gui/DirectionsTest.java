package com.cquests.gui;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;
class DirectionsTest {
    @Test void arrowsFollowThePlayersYaw() {
        assertEquals("↑", Directions.arrow(0, 10, 0));
        assertEquals("→", Directions.arrow(10, 0, 0));
        assertEquals("←", Directions.arrow(-10, 0, 0));
        assertEquals("↓", Directions.arrow(0, -10, 0));
        assertEquals("↑", Directions.arrow(10, 0, -90));
        assertEquals("↑", Directions.arrow(10, 0, 270));
        assertEquals("↗", Directions.arrow(10, 10, 0));
    }
}
