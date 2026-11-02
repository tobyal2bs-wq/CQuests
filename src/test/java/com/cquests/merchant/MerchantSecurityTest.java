package com.cquests.merchant;

import com.cquests.CQuestsPlugin;
import org.bukkit.entity.Player;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class MerchantSecurityTest {
    @Test void currentClientSneakInputIsRecognisedWithoutGrantingOperatorRights(){
        Player player=mock(Player.class);org.bukkit.Input input=mock(org.bukkit.Input.class);when(player.getCurrentInput()).thenReturn(input);
        assertFalse(MerchantService.editGesture(player));when(input.isSneak()).thenReturn(true);
        assertTrue(MerchantService.editGesture(player));assertFalse(MerchantService.canEdit(player));
    }
    @Test void permissionWildcardDoesNotGrantEditingToNonOperator(){
        Player player=mock(Player.class);when(player.hasPermission(anyString())).thenReturn(true);
        assertFalse(MerchantService.canEdit(player));when(player.isOp()).thenReturn(true);assertTrue(MerchantService.canEdit(player));
        when(player.isOp()).thenReturn(false);assertFalse(MerchantService.canEdit(player));
    }
    @Test void directCommandStillRejectsNonOperator(){
        CQuestsPlugin plugin=mock(CQuestsPlugin.class);Player player=mock(Player.class);when(player.hasPermission(anyString())).thenReturn(true);
        new MerchantCommand(plugin).run(player,new String[]{"merchant","edit","rowan"});verify(plugin,never()).merchants();verify(plugin).send(eq(player),contains("Only an operator"));
    }
    @Test void nonOperatorCannotStartDemoThroughCommand(){
        CQuestsPlugin plugin=mock(CQuestsPlugin.class);Player player=mock(Player.class);when(player.hasPermission(anyString())).thenReturn(true);
        new MerchantCommand(plugin).run(player,new String[]{"merchant","test"});verify(plugin,never()).merchants();verify(plugin).send(eq(player),contains("Only an operator"));
    }
    @Test void pointParserRejectsNonFiniteCoordinates(){
        assertNull(MerchantPoint.decode("world;NaN;64;0;0"));assertNull(MerchantPoint.decode("world;0;64;Infinity;0"));
        var p=new MerchantPoint("world",.5,64,.5,90);assertEquals(p,MerchantPoint.decode(p.encode()));
    }
}
