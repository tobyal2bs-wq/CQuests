package com.cquests.dialogue;

import net.kyori.adventure.text.Component;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.List;
import java.util.function.BooleanSupplier;

/** Resuming chat and accepting the last incoming message must be one atomic decision. */
final class SpeechChatBuffer {
    private final ArrayDeque<Component> messages=new ArrayDeque<>();
    private boolean paused=true;

    synchronized boolean defer(Component message,BooleanSupplier removeViewer) {
        // If full, leave the viewer attached to the live message instead of silently dropping it.
        if(!paused||messages.size()>=64||!removeViewer.getAsBoolean())return false;
        messages.addLast(message);
        return true;
    }

    synchronized List<Component> resume() {
        paused=false;
        List<Component> ready=new ArrayList<>(messages);
        messages.clear();
        return ready;
    }
}
