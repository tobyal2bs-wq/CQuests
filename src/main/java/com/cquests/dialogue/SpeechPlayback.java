package com.cquests.dialogue;

import java.util.List;

/** Player-thread dialogue cursor: revealing text and skipping a reading pause are distinct actions. */
final class SpeechPlayback {
    record Frame(String visible, String completed, boolean ready) {}
    private final List<String> sentences;
    private final SpeechTiming timing;
    private int line, letters, pause, wait;
    private boolean reading, finishRequested, ready;

    SpeechPlayback(List<String> sentences, SpeechTiming timing) {
        this.sentences = List.copyOf(sentences);
        this.timing = timing;
    }

    boolean ready() { return ready; }

    /** True means open choices; otherwise finish this sentence or start the next one. */
    boolean click() {
        if (ready || line >= sentences.size()) return true;
        if (reading) {
            reading = false;
            pause = 0;
            wait = 0;
        } else {
            finishRequested = true;
        }
        return false;
    }

    Frame tick() {
        if (reading) {
            if (pause-- > 0) return null;
            reading = false;
            wait = 0;
        }
        if (line >= sentences.size()) {
            if (ready) return null;
            ready = true;
            return new Frame("", null, true);
        }
        if (!finishRequested && wait-- > 0) return null;
        wait = timing.characterTicks() - 1;
        String sentence = sentences.get(line);
        int count = sentence.codePointCount(0, sentence.length());
        letters = finishRequested ? count : Math.min(count, letters + 1);
        finishRequested = false;
        String visible = sentence.substring(0, sentence.offsetByCodePoints(0, letters));
        String completed = null;
        if (letters == count) {
            completed = sentence;
            line++;
            letters = 0;
            reading = true;
            pause = timing.readingTicks();
        }
        return new Frame(visible, completed, false);
    }
}
