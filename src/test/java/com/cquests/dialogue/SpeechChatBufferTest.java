package com.cquests.dialogue;

import net.kyori.adventure.text.Component;
import org.junit.jupiter.api.Test;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import static org.junit.jupiter.api.Assertions.*;

class SpeechChatBufferTest {
    @Test void fullBufferLeavesNextMessageVisibleInsteadOfDroppingIt() {
        var buffer=new SpeechChatBuffer();var hidden=new AtomicInteger();
        for(int i=0;i<64;i++)assertTrue(buffer.defer(Component.text("message "+i),()->{hidden.incrementAndGet();return true;}));
        assertFalse(buffer.defer(Component.text("overflow"),()->{hidden.incrementAndGet();return true;}));
        assertEquals(64,hidden.get());assertEquals(64,buffer.resume().size());
        assertTrue(buffer.resume().isEmpty());
    }
    @Test void finishedSessionCannotHideLateChat() {
        var buffer=new SpeechChatBuffer();buffer.resume();
        assertFalse(buffer.defer(Component.text("late"),()->{fail("late chat must retain its live viewer");return true;}));
    }
    @Test void concurrentResumeEitherFlushesMessageOrLeavesItLive() throws Exception {
        try(var pool=Executors.newFixedThreadPool(2)){
            for(int i=0;i<200;i++){
                var buffer=new SpeechChatBuffer();var start=new CountDownLatch(1);var hidden=new AtomicInteger();
                var offer=pool.submit(()->{start.await();return buffer.defer(Component.text("race"),()->{hidden.incrementAndGet();return true;});});
                var flush=pool.submit(()->{start.await();return buffer.resume();});start.countDown();
                boolean deferred=offer.get(3,TimeUnit.SECONDS);var delivered=flush.get(3,TimeUnit.SECONDS);
                assertEquals(deferred?1:0,hidden.get());assertEquals(deferred?1:0,delivered.size());
                assertTrue(buffer.resume().isEmpty());
            }
        }
    }
}
