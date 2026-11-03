package com.cquests.farm;

import org.bukkit.Bukkit;
import org.bukkit.OfflinePlayer;
import org.bukkit.entity.Player;
import java.lang.reflect.Method;

/**
 * Charges money. By default through Vault. Servers whose economy has no Vault provider can set
 * economy.balance-placeholder (read with PlaceholderAPI) and economy.take-command / give-command in
 * config.yml; then the balance is read from the placeholder and money is moved with those commands.
 */
public final class EconomyBridge {
    private static volatile String balancePlaceholder = "", takeCommand = "", giveCommand = "";
    /** Called on enable and /cq reload. Empty strings mean "use Vault". */
    public static void configure(String placeholder, String take, String give) {
        balancePlaceholder = placeholder == null ? "" : placeholder.trim();
        takeCommand = take == null ? "" : take.trim();
        giveCommand = give == null ? "" : give.trim();
    }
    static boolean custom() { return !takeCommand.isEmpty() && !balancePlaceholder.isEmpty(); }

    /** "$5,000,000.00", "5.2M", "12k", "1 234" -> the number, or NaN when it isn't one. */
    public static double parseAmount(String raw) {
        if (raw == null) return Double.NaN;
        String text = raw.replaceAll("(?i)&[0-9a-fk-or]|\u00a7[0-9a-fk-or]", "").replaceAll("[\\s,$€£_']", "").toLowerCase(java.util.Locale.ROOT);
        double scale = 1;
        if (text.endsWith("k")) { scale = 1e3; text = text.substring(0, text.length() - 1); }
        else if (text.endsWith("m")) { scale = 1e6; text = text.substring(0, text.length() - 1); }
        else if (text.endsWith("b")) { scale = 1e9; text = text.substring(0, text.length() - 1); }
        else if (text.endsWith("t")) { scale = 1e12; text = text.substring(0, text.length() - 1); }
        try { double value = Double.parseDouble(text) * scale; return Double.isFinite(value) ? value : Double.NaN; }
        catch (NumberFormatException e) { return Double.NaN; }
    }

    /** The player's balance, or NaN when no economy can be read. */
    public double balance(Player player) {
        if (!balancePlaceholder.isEmpty() && Bukkit.getPluginManager().isPluginEnabled("PlaceholderAPI")) {
            try { return parseAmount(Papi.apply(player, balancePlaceholder)); } catch (LinkageError | RuntimeException e) { return Double.NaN; }
        }
        refresh(); Binding current = binding; if (current == null) return Double.NaN;
        try { return ((Number) current.api().getMethod("getBalance", OfflinePlayer.class).invoke(current.provider(), player)).doubleValue(); }
        catch (ReflectiveOperationException | RuntimeException e) { return Double.NaN; }
    }

    /** Kept separate so servers without PlaceholderAPI never load its classes. */
    private static final class Papi {
        static String apply(Player player, String text) { return me.clip.placeholderapi.PlaceholderAPI.setPlaceholders(player, text); }
    }

    private static void run(String template, Player player, long amount) {
        String command = template.replace("%player%", player.getName()).replace("<player>", player.getName())
                .replace("%amount%", Long.toString(amount)).replace("<amount>", Long.toString(amount));
        String line = command.startsWith("/") ? command.substring(1) : command;
        com.cquests.util.Sched.global(() -> Bukkit.dispatchCommand(Bukkit.getConsoleSender(), line));
    }
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
    public boolean available(){if(custom())return true;refresh();return binding!=null;}
    public boolean withdraw(Player player,long amount) {
        return charge(player,amount)!=null;
    }
    public static final class Payment {
        private final java.util.function.BooleanSupplier action;
        private final java.util.concurrent.atomic.AtomicBoolean refunded=new java.util.concurrent.atomic.AtomicBoolean();
        private Payment(java.util.function.BooleanSupplier action){this.action=action;}
        public boolean refund(){return refunded.compareAndSet(false,true)&&action.getAsBoolean();}
    }
    public Payment charge(Player player,long amount) {
        if(amount==0)return new Payment(()->true);
        if(amount<0)return null;
        if(custom()){
            double value=balance(player);
            if(!Double.isFinite(value)||value<amount)return null;
            run(takeCommand,player,amount);
            String give=giveCommand;
            return new Payment(()->{if(give.isEmpty())return false;run(give,player,amount);return true;});
        }
        refresh();Binding current=binding;if(current==null)return null;
        try {
            Method balance=current.api().getMethod("getBalance",OfflinePlayer.class);
            double value=((Number)balance.invoke(current.provider(),player)).doubleValue();
            if(!Double.isFinite(value)||value<amount)return null;
            Object result=current.api().getMethod("withdrawPlayer",OfflinePlayer.class,double.class).invoke(current.provider(),player,(double)amount);
            if(!(boolean)result.getClass().getMethod("transactionSuccess").invoke(result))return null;
            return new Payment(()->{
                try{Object response=current.api().getMethod("depositPlayer",OfflinePlayer.class,double.class).invoke(current.provider(),player,(double)amount);
                    return (boolean)response.getClass().getMethod("transactionSuccess").invoke(response);
                }catch(ReflectiveOperationException|RuntimeException e){return false;}
            });
        }catch(ReflectiveOperationException|RuntimeException e){return null;}
    }
}
