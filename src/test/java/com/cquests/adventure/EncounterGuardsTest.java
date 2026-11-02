package com.cquests.adventure;

import com.cquests.CQuestsPlugin;
import org.bukkit.entity.*;
import org.bukkit.event.entity.*;
import org.bukkit.persistence.*;
import org.junit.jupiter.api.Test;
import java.util.*;
import static org.mockito.Mockito.*;

class EncounterGuardsTest {
    private final CQuestsPlugin plugin=mock(CQuestsPlugin.class);
    private final QuestAdventures service;
    EncounterGuardsTest(){when(plugin.getName()).thenReturn("CQuests");service=new QuestAdventures(plugin);}
    private <T extends Entity> T entity(Class<T> type,UUID owner){
        T entity=mock(type);when(entity.getUniqueId()).thenReturn(UUID.randomUUID());
        var pdc=mock(PersistentDataContainer.class);when(entity.getPersistentDataContainer()).thenReturn(pdc);
        when(pdc.get(any(),eq(PersistentDataType.STRING))).thenAnswer(i->{String key=((org.bukkit.NamespacedKey)i.getArgument(0)).getKey();return key.equals("adventure_owner")?(owner==null?null:owner.toString()):"boss";});
        return entity;
    }
    @Test void bossAndItsSkullsCannotDamageBystandersButCanDamageOwner(){
        UUID id=UUID.randomUUID();var boss=entity(Wither.class,id);var bystander=entity(Player.class,null);
        var blocked=mock(EntityDamageByEntityEvent.class);when(blocked.getDamager()).thenReturn(boss);when(blocked.getEntity()).thenReturn(bystander);
        service.damage(blocked);verify(blocked).setCancelled(true);
        var owner=entity(Player.class,null);when(owner.getUniqueId()).thenReturn(id);
        var allowed=mock(EntityDamageByEntityEvent.class);when(allowed.getDamager()).thenReturn(boss);when(allowed.getEntity()).thenReturn(owner);
        service.damage(allowed);verify(allowed,never()).setCancelled(true);
        var skull=entity(WitherSkull.class,id);when(skull.getShooter()).thenReturn(boss);
        when(blocked.getDamager()).thenReturn(skull);service.damage(blocked);verify(blocked,times(2)).setCancelled(true);
    }
    @Test void onlyOwnerOrOwnerProjectileCanDamageTheirVessel(){
        UUID id=UUID.randomUUID();var boss=entity(Wither.class,id);var stranger=entity(Player.class,null);
        var hit=mock(EntityDamageByEntityEvent.class);when(hit.getDamager()).thenReturn(stranger);when(hit.getEntity()).thenReturn(boss);
        service.damage(hit);verify(hit).setCancelled(true);
        var owner=entity(Player.class,null);when(owner.getUniqueId()).thenReturn(id);
        var arrow=entity(Arrow.class,null);when(arrow.getShooter()).thenReturn(owner);
        var allowed=mock(EntityDamageByEntityEvent.class);when(allowed.getDamager()).thenReturn(arrow);when(allowed.getEntity()).thenReturn(boss);
        service.damage(allowed);verify(allowed,never()).setCancelled(true);
    }
    @Test void retargetingAndTerrainDamageAreDenied(){
        var boss=entity(Wither.class,UUID.randomUUID());var bystander=entity(Player.class,null);
        var target=mock(EntityTargetLivingEntityEvent.class);when(target.getEntity()).thenReturn(boss);when(target.getTarget()).thenReturn(bystander);
        service.target(target);verify(target).setCancelled(true);
        var explode=mock(EntityExplodeEvent.class);when(explode.getEntity()).thenReturn(boss);var blocks=new ArrayList<org.bukkit.block.Block>();blocks.add(mock(org.bukkit.block.Block.class));when(explode.blockList()).thenReturn(blocks);
        service.explode(explode);org.junit.jupiter.api.Assertions.assertTrue(blocks.isEmpty());verify(explode).setYield(0);
    }
}
