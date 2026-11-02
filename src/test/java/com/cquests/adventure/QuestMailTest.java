package com.cquests.adventure;

import com.cquests.data.PlayerData;
import org.junit.jupiter.api.Test;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;

class QuestMailTest {
    private QuestMail.Letter letter(String choice){return new QuestMail.Letter("steve","Steve","A promise","story_martha",choice,"martha",750,List.of("A letter."));}
    @Test void letterRequiresItsQuestMeetingHarvestAndExactDecision(){
        var data=new PlayerData(UUID.randomUUID());assertFalse(letter("kind").eligible(data));
        data.meet("martha");data.addWheat(750);assertFalse(letter("kind").eligible(data));
        data.complete("story_martha",true);assertFalse(letter("kind").eligible(data));
        data.decide("story_martha","kind");assertTrue(letter("kind").eligible(data));assertFalse(letter("selfish").eligible(data));
    }
    @Test void readingIsIdempotentAndDoesNotPayOrCompleteQuests(){
        var data=new PlayerData(UUID.randomUUID());data.addWheat(750);
        assertTrue(data.readLetter("steve"));assertFalse(data.readLetter("steve"));
        assertEquals(1,data.sunflowers());assertEquals(0,data.skillXp());assertEquals(0,data.completedCount());
        assertFalse(data.readLetter("../bad"));assertFalse(data.readLetter("a.b"));
    }
    @Test void readLedgerIsBounded(){
        var data=new PlayerData(UUID.randomUUID());for(int i=0;i<512;i++)assertTrue(data.readLetter("letter_"+i));
        assertFalse(data.readLetter("too_many"));assertTrue(data.letterRead("letter_511"));
    }
    @Test void sunflowerSpendingCannotOverdrawOrAcceptNegativePrices(){
        var data=new PlayerData(UUID.randomUUID());data.addWheat(1499);assertEquals(1,data.sunflowers());
        assertFalse(data.spendSunflowers(-1));assertFalse(data.spendSunflowers(2));assertTrue(data.spendSunflowers(1));
        assertFalse(data.spendSunflowers(1));assertEquals(0,data.sunflowers());
        data.addWheat(1);assertEquals(1,data.sunflowers());data.refundSunflowers(1);assertEquals(2,data.sunflowers());
        data.refundSunflowers(1);assertEquals(2,data.sunflowers());
    }
    @Test void storyResetDoesNotRestoreSpentCurrencyOrOverflowHarvestCount(){
        var data=new PlayerData(UUID.randomUUID());data.addWheat(1500);data.spendSunflowers(1);data.reset();assertEquals(1,data.sunflowers());
        data.addWheat(Long.MAX_VALUE);data.addWheat(1);assertEquals(Long.MAX_VALUE,data.wheatHarvested());assertTrue(data.sunflowers()>0);
    }
}
