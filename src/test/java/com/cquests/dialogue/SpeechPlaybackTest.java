package com.cquests.dialogue;

import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

class SpeechPlaybackTest {
    private SpeechPlayback playback() {
        return new SpeechPlayback(List.of("First.", "Middle.", "Last."), new SpeechTiming(2, 80));
    }

    private SpeechPlayback.Frame nextFrame(SpeechPlayback speech) {
        for (int i = 0; i < 500; i++) {
            var frame = speech.tick();
            if (frame != null) return frame;
        }
        throw new AssertionError("Speech did not advance");
    }

    @Test void everySentenceTypesProgressivelyWithoutClicks() {
        var speech = playback();
        for (String sentence : List.of("First.", "Middle.", "Last.")) {
            for (int i = 1; i <= sentence.length(); i++) {
                var frame = nextFrame(speech);
                assertEquals(sentence.substring(0, i), frame.visible());
                assertEquals(i == sentence.length() ? sentence : null, frame.completed());
            }
        }
        assertTrue(nextFrame(speech).ready());
        assertTrue(speech.click());
    }

    @Test void clickFinishesOnlyCurrentSentenceAndNextClickSkipsPause() {
        var speech = playback();
        assertEquals("F", speech.tick().visible());
        assertFalse(speech.click());
        assertEquals("First.", speech.tick().completed());
        assertNull(speech.tick());
        assertFalse(speech.click());
        assertEquals("M", speech.tick().visible());
        assertNull(speech.tick());
        assertEquals("Mi", speech.tick().visible());
    }

    @Test void clickAtEndOfPauseDoesNotFinishTheNextSentence() {
        var speech = playback();
        speech.click();
        assertEquals("First.", speech.tick().completed());
        for (int i = 0; i < 80; i++) assertNull(speech.tick());
        assertFalse(speech.click());
        assertEquals("M", speech.tick().visible());
    }

    @Test void clickAfterLastSentenceOpensChoicesWithoutWaiting() {
        var speech = new SpeechPlayback(List.of("Done."), new SpeechTiming(2, 400));
        speech.click();
        assertEquals("Done.", speech.tick().completed());
        assertTrue(speech.click());
    }

    @Test void repeatedFinishClicksDoNotConsumeOrLeakIntoAnotherSentence() {
        var speech = playback();
        for (int i = 0; i < 20; i++) assertFalse(speech.click());
        assertEquals("First.", speech.tick().completed());
        assertFalse(speech.click());
        assertEquals("M", speech.tick().visible());
    }

    @Test void unicodeIsRevealedAsWholeCodePoints() {
        var speech = new SpeechPlayback(List.of("😀Hi"), new SpeechTiming(1, 20));
        assertEquals("😀", speech.tick().visible());
        assertEquals("😀H", speech.tick().visible());
        assertEquals("😀Hi", speech.tick().completed());
    }
}
