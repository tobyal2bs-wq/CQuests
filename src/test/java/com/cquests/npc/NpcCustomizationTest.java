package com.cquests.npc;

import com.cquests.CQuestsPlugin;
import com.cquests.merchant.MerchantService;
import com.cquests.model.NpcDef;
import org.bukkit.entity.Player;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.io.File;
import java.nio.file.Files;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class NpcCustomizationTest {
    @Test void cosmeticOverridesPreserveIdsQuestLevelAndAppearance(@TempDir File folder)throws Exception{
        Files.writeString(new File(folder,"characters.yml").toPath(),"characters:\n  bob:\n    name: '<gold>B.O.B'\n    prefix: '[Guide] '\n    intro: ['I remember you.']\n  pip:\n    name: Pip the Brave\n");
        var plugin=mock(CQuestsPlugin.class);when(plugin.getDataFolder()).thenReturn(folder);
        var editor=new NpcCustomization(plugin);try{
            var original=new NpcDef("bob","Bob","old","FARMER","PLAINS",400,2,true,false,false,"Notch",List.of("Old"),List.of("Wait"));
            var edited=editor.apply(original);assertEquals("bob",edited.id());assertEquals(400,edited.level());assertEquals("Notch",edited.playerSkin());
            assertEquals(List.of("I remember you."),edited.intro());assertEquals(List.of("Wait"),edited.idle());assertEquals("[Guide] <gold>B.O.B",editor.label("bob","default"));
            assertEquals("Pip the Brave",editor.text("companion_123","name","Pip"));
        }finally{editor.shutdown();}
    }
    @Test void wildcardPermissionDoesNotLetNonOperatorChangeCharacters(@TempDir File folder){
        var plugin=mock(CQuestsPlugin.class);when(plugin.getDataFolder()).thenReturn(folder);var player=mock(Player.class);when(player.hasPermission(anyString())).thenReturn(true);
        var editor=new NpcCustomization(plugin);try{
            editor.command(player,new String[]{"character","bob","name","Fake"});
            verify(plugin,never()).npcs();assertEquals("Bob",editor.text("bob","name","Bob"));
        }finally{editor.shutdown();}
    }
    @Test void queuedEditsDrainAndResetRestoresDefaults(@TempDir File folder){
        var plugin=mock(CQuestsPlugin.class);when(plugin.getDataFolder()).thenReturn(folder);
        var registry=mock(NpcRegistry.class);when(plugin.npcs()).thenReturn(registry);when(plugin.merchants()).thenReturn(mock(MerchantService.class));when(plugin.nameplates()).thenReturn(mock(NpcNameplates.class));
        var npc=new NpcDef("bob","Bob","","NONE","PLAINS",400,2,true,false,false,"",List.of(),List.of());when(registry.get("bob")).thenReturn(npc);
        var player=mock(Player.class);when(player.isOp()).thenReturn(true);var editor=new NpcCustomization(plugin);
        editor.command(player,new String[]{"character","bob","name","B.O.B"});editor.command(player,new String[]{"character","bob","prefix","<gold>[Guide] "});editor.shutdown();
        var restart=new NpcCustomization(plugin);assertEquals("B.O.B",restart.text("bob","name","Bob"));assertTrue(restart.text("bob","prefix","").contains("Guide"));
        restart.command(player,new String[]{"character","bob","reset"});restart.shutdown();
        var finalRead=new NpcCustomization(plugin);try{assertEquals("Bob",finalRead.text("bob","name","Bob"));}finally{finalRead.shutdown();}
    }
}
