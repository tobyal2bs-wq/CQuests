package com.cquests.merchant;

import org.bukkit.inventory.ItemStack;

/** Detached offer values; GUI preview lore never changes the real item templates. */
public record TradeOffer(ItemStack first,ItemStack second,ItemStack reward,long money) {
    public TradeOffer {
        first=copy(first);second=copy(second);reward=copy(reward);
        if(money<0||money>1_000_000_000L)throw new IllegalArgumentException("Money price must be 0–1,000,000,000");
        if(reward==null||(first==null&&second==null&&money==0))throw new IllegalArgumentException("Set a reward and at least one cost");
    }
    private static ItemStack copy(ItemStack item){
        if(empty(item))return null;
        if(item.getAmount()<1||item.getAmount()>item.getMaxStackSize())throw new IllegalArgumentException("Use legal item stack sizes");
        return item.clone();
    }
    public static boolean empty(ItemStack item){return item==null||item.getType()==org.bukkit.Material.AIR||item.getType()==org.bukkit.Material.CAVE_AIR||item.getType()==org.bukkit.Material.VOID_AIR;}
    public ItemStack first(){return copy(first);}public ItemStack second(){return copy(second);}public ItemStack reward(){return copy(reward);}
}
