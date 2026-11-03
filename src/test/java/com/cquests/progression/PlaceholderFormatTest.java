package com.cquests.progression;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class PlaceholderFormatTest {
    @Test
    void shortNumbers() {
        assertEquals("0", SkillPlaceholders.compact(0));
        assertEquals("999", SkillPlaceholders.compact(999));
        assertEquals("1K", SkillPlaceholders.compact(1000));
        assertEquals("1.2K", SkillPlaceholders.compact(1250));
        assertEquals("34.5K", SkillPlaceholders.compact(34_567));
        assertEquals("999K", SkillPlaceholders.compact(999_999));
        assertEquals("1M", SkillPlaceholders.compact(1_000_000));
        assertEquals("1.5B", SkillPlaceholders.compact(1_500_000_000L));
        assertEquals("-2K", SkillPlaceholders.compact(-2000));
        SkillPlaceholders.compact(Long.MAX_VALUE);
        SkillPlaceholders.compact(Long.MIN_VALUE);
    }
}
