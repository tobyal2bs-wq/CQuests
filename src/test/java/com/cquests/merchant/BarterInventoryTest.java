package com.cquests.merchant;

import org.bukkit.Material;
import org.bukkit.inventory.ItemStack;
import org.junit.jupiter.api.Test;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class BarterInventoryTest {
    @Test void sunflowerOnlyOfferIsValidAndStillRequiresInventorySpace(){
        var offer=new TradeOffer(null,null,stack(Material.DIAMOND,1),0,2);
        assertEquals(2,offer.sunflowers());assertNotNull(BarterInventory.exchange(new ItemStack[1],offer));
        assertNull(BarterInventory.exchange(new ItemStack[]{stack(Material.STONE,64)},offer));
        assertThrows(IllegalArgumentException.class,()->new TradeOffer(null,null,stack(Material.DIAMOND,1),0,-1));
    }
    private static final Map<ItemStack,String> tags=Collections.synchronizedMap(new IdentityHashMap<>());
    // ItemStack's matching/cloning contract without a running server registry.
    private static ItemStack stack(Material type,int count,String tag){
        ItemStack item=mock(ItemStack.class);AtomicInteger amount=new AtomicInteger(count);tags.put(item,tag);
        when(item.getType()).thenReturn(type);when(item.getMaxStackSize()).thenReturn(64);when(item.getAmount()).thenAnswer(i->amount.get());
        doAnswer(i->{amount.set(i.getArgument(0));return null;}).when(item).setAmount(anyInt());
        when(item.clone()).thenAnswer(i->stack(type,amount.get(),tag));
        when(item.isSimilar(any())).thenAnswer(i->{ItemStack other=i.getArgument(0);return other!=null&&other.getType()==type&&Objects.equals(tags.get(other),tag);});return item;
    }
    private static ItemStack stack(Material type,int count){return stack(type,count,"");}
    @Test void overlappingCostsCannotSpendTheSameItemsTwice(){
        ItemStack[] before={stack(Material.IRON_INGOT,48)};
        var offer=new TradeOffer(stack(Material.IRON_INGOT,32),stack(Material.IRON_INGOT,32),stack(Material.DIAMOND,1),0);
        assertNull(BarterInventory.exchange(before,offer));assertEquals(48,before[0].getAmount());
    }
    @Test void bothCostsAreRemovedAndRewardUsesFreedSlot(){
        ItemStack[] before={stack(Material.WHEAT,32),stack(Material.COAL,8)};
        var offer=new TradeOffer(stack(Material.WHEAT,32),stack(Material.COAL,8),stack(Material.BREAD,16),50);
        ItemStack[] after=BarterInventory.exchange(before,offer);assertNotNull(after);assertEquals(Material.BREAD,after[0].getType());assertEquals(16,after[0].getAmount());assertNull(after[1]);
        assertEquals(32,before[0].getAmount());assertEquals(8,before[1].getAmount());
    }
    @Test void fullInventoryDeclinesBeforeAnyRealCostIsRemoved(){
        ItemStack[] before={stack(Material.WHEAT,64),stack(Material.STONE,64)};
        var offer=new TradeOffer(stack(Material.WHEAT,1),null,stack(Material.DIAMOND,1),0);
        assertNull(BarterInventory.exchange(before,offer));assertEquals(64,before[0].getAmount());
    }
    @Test void customMetadataCannotImpersonatePlainCost(){
        var offer=new TradeOffer(stack(Material.IRON_INGOT,1),null,stack(Material.DIAMOND,1),0);
        assertNull(BarterInventory.exchange(new ItemStack[]{stack(Material.IRON_INGOT,1,"bound-owner")},offer));
    }
    @Test void rewardCannotOverflowItsStack(){
        var offer=new TradeOffer(stack(Material.WHEAT,1),null,stack(Material.WHEAT,2),0);
        assertNull(BarterInventory.exchange(new ItemStack[]{stack(Material.WHEAT,64)},offer));
    }
    @Test void moneyOnlyOfferNeedsSpaceButNoItemCost(){
        var offer=new TradeOffer(null,null,stack(Material.DIAMOND,1),100);
        assertNotNull(BarterInventory.exchange(new ItemStack[2],offer));
        assertThrows(IllegalArgumentException.class,()->new TradeOffer(null,null,stack(Material.DIAMOND,1),0));
    }
    @Test void editingCallerOrPreviewDoesNotChangeOffer(){
        ItemStack sample=stack(Material.WHEAT,32);var offer=new TradeOffer(sample,null,stack(Material.BREAD,8),0);sample.setAmount(1);offer.first().setAmount(2);assertEquals(32,offer.first().getAmount());
    }
}
