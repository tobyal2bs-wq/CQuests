package com.cquests.progression;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class NumberFormatTest {
    @Test
    void shortNumbers() {
        assertEquals("0", com.cquests.util.Text.compact(0));
        assertEquals("999", com.cquests.util.Text.compact(999));
        assertEquals("1K", com.cquests.util.Text.compact(1000));
        assertEquals("1.2K", com.cquests.util.Text.compact(1250));
        assertEquals("34.5K", com.cquests.util.Text.compact(34_567));
        assertEquals("999K", com.cquests.util.Text.compact(999_999));
        assertEquals("1M", com.cquests.util.Text.compact(1_000_000));
        assertEquals("1.5B", com.cquests.util.Text.compact(1_500_000_000L));
        assertEquals("-2K", com.cquests.util.Text.compact(-2000));
        com.cquests.util.Text.compact(Long.MAX_VALUE);
        com.cquests.util.Text.compact(Long.MIN_VALUE);
    }
}
