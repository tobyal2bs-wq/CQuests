package com.cquests.npc;

import com.cquests.CQuestsPlugin;
import com.cquests.util.Text;
import net.kyori.adventure.text.format.NamedTextColor;
import net.kyori.adventure.text.Component;
import org.junit.jupiter.api.Test;
import java.util.UUID;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class NpcNameplatesTest {
    @Test void uppercaseKeepsColoursAndPunctuation(){
        var input=Component.text("B.o.b",NamedTextColor.GOLD).append(Component.text(" level 5",NamedTextColor.AQUA));
        var result=NpcNameplates.uppercase(input);assertEquals("B.O.B LEVEL 5",Text.plain(result));
        assertEquals(NamedTextColor.GOLD,result.color());assertEquals(NamedTextColor.AQUA,result.children().getFirst().color());
    }
    @Test void nameplateStaysRaisedUntilBothConversationsEnd(){
        var plates=new NpcNameplates(mock(CQuestsPlugin.class));UUID first=UUID.randomUUID(),second=UUID.randomUUID();
        assertEquals(2.45,plates.height("stephan"));plates.begin("stephan",first);plates.begin("stephan",second);
        assertEquals(3.85,plates.height("stephan"));plates.end("stephan",first);assertEquals(3.85,plates.height("stephan"));
        plates.end("stephan",first);assertEquals(3.85,plates.height("stephan"));plates.end("stephan",second);assertEquals(2.45,plates.height("stephan"));
    }
}
