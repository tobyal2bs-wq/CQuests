package com.cquests.merchant;

import org.bukkit.inventory.ItemStack;

/** Simulates the entire barter before touching the player: no partial costs or ground drops. */
public final class BarterInventory {
    private BarterInventory(){}
    public static ItemStack[] exchange(ItemStack[] contents,TradeOffer offer){
        ItemStack[] next=new ItemStack[contents.length];for(int i=0;i<contents.length;i++)next[i]=contents[i]==null?null:contents[i].clone();
        if(!take(next,offer.first())||!take(next,offer.second())||!give(next,offer.reward()))return null;
        return next;
    }
    private static boolean take(ItemStack[] contents,ItemStack cost){
        if(cost==null)return true;int left=cost.getAmount();
        for(int i=0;i<contents.length&&left>0;i++){
            ItemStack item=contents[i];if(item==null||!item.isSimilar(cost))continue;
            int n=Math.min(left,item.getAmount());left-=n;
            if(n==item.getAmount())contents[i]=null;else item.setAmount(item.getAmount()-n);
        }
        return left==0;
    }
    private static boolean give(ItemStack[] contents,ItemStack reward){
        int left=reward.getAmount(),max=reward.getMaxStackSize();
        for(ItemStack item:contents)if(item!=null&&item.isSimilar(reward)){
            int n=Math.min(left,Math.max(0,max-item.getAmount()));item.setAmount(item.getAmount()+n);left-=n;
        }
        for(int i=0;i<contents.length&&left>0;i++)if(TradeOffer.empty(contents[i])){
            ItemStack item=reward.clone();int n=Math.min(left,max);item.setAmount(n);contents[i]=item;left-=n;
        }
        return left==0;
    }
}
