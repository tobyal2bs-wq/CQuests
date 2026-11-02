package com.cquests.data;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.io.File;
import java.util.UUID;
import java.util.logging.Logger;
import static org.junit.jupiter.api.Assertions.*;

class CorrespondenceTest {
    @Test void deliveryTimeNeverChangesWhenRereading(){var d=new PlayerData(UUID.randomUUID());assertEquals(1000,d.receiveMail("letter",1000));assertEquals(1000,d.receiveMail("letter",9000));assertEquals(0,d.receiveMail("../bad",9000));}
    @Test void historyRetainsNewestFortyAndDoesNotChangeQuestOrCurrency(){var d=new PlayerData(UUID.randomUUID());d.addWheat(750);for(int i=0;i<50;i++)d.addMail(new MailEntry("letter","Bob","Reply "+i,1,false));assertEquals(40,d.mailThread().size());assertEquals("Reply 10",d.mailThread().getFirst().text());assertEquals(1,d.sunflowers());assertEquals(0,d.completedCount());}
    @Test void aiLimitsSurviveReconnectAndClockRollback(@TempDir File folder){
        long now=1_800_000_000_000L;UUID id=UUID.randomUUID();var store=new PlayerStore(folder,Logger.getLogger("correspondence"));var d=store.get(id);
        assertTrue(d.reserveAi(now,2));assertFalse(d.reserveAi(now+1000,2));assertTrue(d.reserveAi(now+30001,2));assertFalse(d.reserveAi(now+60002,2));
        d.receiveMail("letter",now);d.addMail(new MailEntry("letter","Bob","I remember.",now,false));store.saveAllNow();
        var loaded=new PlayerStore(folder,Logger.getLogger("correspondence")).get(id);assertEquals(now,loaded.mailReceived("letter"));assertEquals("I remember.",loaded.mailThread().getFirst().text());assertFalse(loaded.reserveAi(now+60002,2));assertFalse(loaded.reserveAi(now-86_400_000L,2));
    }
    @Test void mailIdsAndSizesAreValidated(){assertThrows(IllegalArgumentException.class,()->new MailEntry("a.b","Bob","text",1,false));assertEquals(1800,new MailEntry("letter","Bob","a".repeat(2000),1,false).text().length());}
}
