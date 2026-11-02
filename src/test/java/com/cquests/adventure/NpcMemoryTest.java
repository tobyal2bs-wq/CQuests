package com.cquests.adventure;

import com.cquests.data.PlayerData;
import org.junit.jupiter.api.Test;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;

class NpcMemoryTest {
    private final NpcMemory.Decision decision=new NpcMemory.Decision("story_martha","martha",List.of("steve"),"Choose","Yes","No","warm","wary","family warm","family wary");
    @Test void choicesRequireCompletedQuestArePermanentAndPrivateToPlayer(){
        var first=new PlayerData(UUID.randomUUID());var other=new PlayerData(UUID.randomUUID());
        assertFalse(first.decide("story_martha","kind"));
        first.complete("story_martha",true);
        assertFalse(first.decide("story_martha","fabricated"));
        assertTrue(first.decide("story_martha","selfish"));assertFalse(first.decide("story_martha","kind"));
        assertEquals("wary",NpcMemory.remember(first,"martha",List.of(decision)));
        assertEquals("family wary",NpcMemory.remember(first,"steve",List.of(decision)));
        assertNull(NpcMemory.remember(first,"jerry",List.of(decision)));
        assertNull(NpcMemory.remember(other,"martha",List.of(decision)));
        first.reset();assertNull(first.decision("story_martha"));
    }
    @Test void kindnessReachesOnlyNamedRelatives(){
        var data=new PlayerData(UUID.randomUUID());data.complete("story_martha",true);assertTrue(data.decide("story_martha","kind"));
        assertEquals("warm",NpcMemory.remember(data,"martha",List.of(decision)));
        assertEquals("family warm",NpcMemory.remember(data,"steve",List.of(decision)));
        assertThrows(UnsupportedOperationException.class,()->data.decisions().put("a","b"));
    }
}
