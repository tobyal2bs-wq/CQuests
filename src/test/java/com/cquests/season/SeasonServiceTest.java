package com.cquests.season;

import org.junit.jupiter.api.Test;

import java.time.LocalDate;
import java.time.MonthDay;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class SeasonServiceTest {
    @Test
    void seasonsRunBetweenTheirDatesAlsoOverNewYear() {
        MonthDay from = MonthDay.of(10, 15), to = MonthDay.of(11, 5);
        assertTrue(SeasonService.inWindow(from, to, LocalDate.of(2026, 10, 31)));
        assertTrue(SeasonService.inWindow(from, to, LocalDate.of(2026, 11, 5)));
        assertFalse(SeasonService.inWindow(from, to, LocalDate.of(2026, 11, 6)));
        MonthDay winter = MonthDay.of(12, 10), end = MonthDay.of(1, 5);
        assertTrue(SeasonService.inWindow(winter, end, LocalDate.of(2026, 12, 25)));
        assertTrue(SeasonService.inWindow(winter, end, LocalDate.of(2027, 1, 2)));
        assertFalse(SeasonService.inWindow(winter, end, LocalDate.of(2027, 2, 1)));
    }
}
