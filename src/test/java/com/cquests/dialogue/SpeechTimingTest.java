package com.cquests.dialogue;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class SpeechTimingTest {
    @Test void slowDefaultsAndUnsafeConfigAreBounded(){
        var normal=new SpeechTiming(2,80);assertEquals(2,normal.characterTicks());assertEquals(80,normal.readingTicks());
        assertEquals(new SpeechTiming(1,20),new SpeechTiming(-10,-10));assertEquals(new SpeechTiming(10,400),new SpeechTiming(10000,10000));
    }
    @Test void longUnicodeSentencesKeepNameplateClearWithoutBreakingCharacters(){
        String line="😀".repeat(250)+". Next sentence.";var parts=SpeechTiming.sentences(line);
        assertTrue(parts.size()>2);assertTrue(parts.stream().allMatch(s->s.codePointCount(0,s.length())<=120));
        assertEquals(line,String.join("",parts.subList(0,3))+" "+parts.get(3));
    }
}
