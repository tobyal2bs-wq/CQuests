package com.cquests.farm;

import com.cquests.T;

import com.cquests.CQuestsPlugin;
import com.cquests.npc.WorldGuardHook;
import com.cquests.util.Text;
import org.bukkit.*;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.persistence.PersistentDataType;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public final class FarmCommand {
    private record Selection(String id,boolean outside,String world,List<Polygon.Vertex> vertices) {}
    private final CQuestsPlugin plugin;private final NamespacedKey key;
    private final Map<UUID,Selection> selections=new ConcurrentHashMap<>();
    public FarmCommand(CQuestsPlugin p){plugin=p;key=new NamespacedKey(p,"farm_wand");}
    public boolean wand(ItemStack item){return item!=null&&item.hasItemMeta()&&item.getItemMeta().getPersistentDataContainer().has(key,PersistentDataType.STRING);}
    public void point(Player player,org.bukkit.block.Block block,boolean undo) {
        Selection s=selections.get(player.getUniqueId());if(s==null)return;
        if(!s.world.equals(block.getWorld().getName())){plugin.send(player,T.t("farm-command.keep-one-outline-in-one", "<red>Keep one outline in one world."));return;}
        if(undo){if(!s.vertices.isEmpty())s.vertices.remove(s.vertices.size()-1);}
        else {
            if(s.vertices.size()>=128){plugin.send(player,T.t("farm-command.maximum-128-outline-points", "<red>Maximum 128 outline points."));return;}
            var v=new Polygon.Vertex(block.getX(),block.getZ());
            if(s.vertices.isEmpty()||!s.vertices.get(s.vertices.size()-1).equals(v))s.vertices.add(v);
        }
        player.spawnParticle(Particle.COMPOSTER,block.getLocation().add(.5,1,.5),6,.15,.15,.15,0);
        plugin.send(player,T.t("farm-command.perimeter-points-cq-farm-save", "<aqua><size> perimeter points <gray>• /cq farm save <arena> <WorldGuard region>", "size", s.vertices.size(), "arena", s.id));
    }
    public void run(CommandSender sender,String[] args){
        if(!(sender instanceof Player p)){sender.sendMessage("Run the farm editor in game.");return;}
        String action=args.length>1?args[1].toLowerCase(Locale.ROOT):"help";
        if(action.equals("menu")){plugin.send(p,T.t("farm-command.use-cq-farm-anvil-to", "<yellow>Use /cq farm anvil to get a Fieldsmith Anvil, then place and right-click it."));return;}
        if(action.equals("anvil")){
            if(!p.isOp()){plugin.send(p,T.t("farm-command.only-ops-can-obtain-a", "<red>Only OPs can obtain a Fieldsmith Anvil."));return;}
            if(p.getInventory().firstEmpty()<0){plugin.send(p,T.t("farm-command.make-room-in-your-inventory", "<yellow>Make room in your inventory first."));return;}
            p.getInventory().addItem(plugin.farm().anvilItem());plugin.send(p,T.t("farm-command.place-the-fieldsmith-anvil-on", "<green>Place the Fieldsmith Anvil on solid ground. Players can right-click it to upgrade hoes."));return;
        }
        if(action.equals("bind")){
            if(!p.isOp()){plugin.send(p,T.t("farm-command.only-ops-can-bind-a", "<red>Only OPs can bind a Fieldsmith Anvil."));return;}
            var block=p.getTargetBlockExact(6);
            if(block==null||!block.getType().name().endsWith("ANVIL")){plugin.send(p,T.t("farm-command.look-at-the-anvil-you", "<red>Look at the anvil you want to bind."));return;}
            plugin.farm().addUpgrader(block.getLocation());plugin.send(p,T.t("farm-command.field-workshop-bound-to-this", "<green>Field workshop bound to this anvil."));return;
        }
        if((action.equals("wand")||action.equals("outside"))&&args.length>=3){
            String id=args[2].toLowerCase(Locale.ROOT);
            if(!id.matches("[a-z0-9_-]{1,40}")){plugin.send(p,T.t("farm-command.use-a-short-area-id", "<red>Use a short area ID with letters, digits, underscores or hyphens."));return;}
            selections.put(p.getUniqueId(),new Selection(id,action.equals("outside"),p.getWorld().getName(),new ArrayList<>()));
            var item=new ItemStack(Material.STICK);item.editMeta(meta->{
                meta.displayName(Text.mm(action.equals("outside")?"<light_purple><bold>Outside outline":"<aqua><bold>Inside outline"));
                meta.lore(List.of(Text.mm(T.t("farm-command.left-click-perimeter-points-in", "<gray>Left click perimeter points in order.")),Text.mm(T.t("farm-command.right-click-to-undo-the", "<gray>Right click to undo the last point."))));
                meta.getPersistentDataContainer().set(key,PersistentDataType.STRING,id);
            });
            p.getInventory().addItem(item);plugin.send(p,T.t("farm-command.select-at-least-three-outline", "<white>Select at least three outline points. <included>", "included", (action.equals("outside")?"The outside stays bounded by the named WG region.":"The inside will be included.")));return;
        }
        if(action.equals("save")&&args.length>=4){
            var s=selections.get(p.getUniqueId());
            if(s==null||!s.id.equalsIgnoreCase(args[2])){plugin.send(p,T.t("farm-command.select-this-area-s-outline", "<red>Select this area's outline first."));return;}
            if(!s.world.equals(p.getWorld().getName())){plugin.send(p,T.t("farm-command.return-to-the-world-where", "<red>Return to the world where you selected this outline."));return;}
            int[] bounds=WorldGuardHook.bounds(p.getWorld(),args[3]);
            if(bounds==null||args[3].equalsIgnoreCase("__global__")){plugin.send(p,T.t("farm-command.use-an-existing-named-worldguard", "<red>Use an existing named WorldGuard region."));return;}
            try{
                Polygon polygon=new Polygon(s.vertices);
                plugin.farm().saveArea(s.id,s.world,args[3],polygon,s.outside,bounds);
                selections.remove(p.getUniqueId());plugin.send(p,T.t("farm-command.saved-in-wg-region-players", "<green>Saved <arena> in WG region <args>. Players get a free farm hoe when they walk in and harvest mature wheat by left-clicking it in survival mode; normal breaking is blocked there.", "arena", Text.escape(s.id), "args", Text.escape(args[3])));
            }catch(RuntimeException e){plugin.send(p,"<red>"+Text.escape(e.getMessage()));}
            return;
        }
        plugin.send(p,T.t("farm-command.cq-farm-wand-include-outline", "<white>/cq farm wand <id> <gray>• include outline\n<white>/cq farm outside <id> <gray>• WG region minus outline\n<white>/cq farm save <id> <wg-region>\n<white>/cq farm anvil <gray>• OP: get a Fieldsmith Anvil\n<white>/cq farm bind <gray>• OP: bind an existing anvil"));
    }
    public void forget(Player p){selections.remove(p.getUniqueId());}
}
