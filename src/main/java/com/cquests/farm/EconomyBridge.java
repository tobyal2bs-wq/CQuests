package com.cquests.farm;

import org.bukkit.Bukkit;
import org.bukkit.OfflinePlayer;
import org.bukkit.entity.Player;
import java.lang.reflect.Method;

/** Charges through the same Vault economy backing vault_eco placeholders; never guesses balances from formatted text. */
public final class EconomyBridge {
    private record Binding(Class<?> api,Object provider) {}
    private volatile Binding binding;
    public void refresh() {
        Binding found=null;
        try {
            Class<?> api=Class.forName("net.milkbowl.vault.economy.Economy");
            @SuppressWarnings({"unchecked","rawtypes"}) var registration=Bukkit.getServicesManager().getRegistration((Class)api);
            if(registration!=null)found=new Binding(api,registration.getProvider());
        }catch(ClassNotFoundException|LinkageError ignored){}
        binding=found;
    }
    public boolean available(){refresh();return binding!=null;}
    public boolean withdraw(Player player,long amount) {
        if(amount==0)return true;
        if(amount<0)return false;
        refresh();Binding current=binding;if(current==null)return false;
        try {
            Method balance=current.api().getMethod("getBalance",OfflinePlayer.class);
            double value=((Number)balance.invoke(current.provider(),player)).doubleValue();
            if(!Double.isFinite(value)||value<amount)return false;
            Object result=current.api().getMethod("withdrawPlayer",OfflinePlayer.class,double.class).invoke(current.provider(),player,(double)amount);
            return (boolean)result.getClass().getMethod("transactionSuccess").invoke(result);
        }catch(ReflectiveOperationException|RuntimeException e){return false;}
    }
}
