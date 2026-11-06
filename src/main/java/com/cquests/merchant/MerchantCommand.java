package com.cquests.merchant;

import com.cquests.T;

import com.cquests.CQuestsPlugin;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;

public final class MerchantCommand {
    private final CQuestsPlugin plugin;public MerchantCommand(CQuestsPlugin plugin){this.plugin=plugin;}
    public void run(CommandSender sender,String[] args){
        if(!(sender instanceof Player p)||!MerchantService.canEdit(p)){plugin.send(sender,T.t("merchant-command.only-an-operator-in-game", "<red>Only an operator in game can configure merchants."));return;}
        String action=args.length>1?args[1].toLowerCase(java.util.Locale.ROOT):"help";
        if(action.equals("test")){plugin.merchants().test(p,args.length>2?args[2].toLowerCase(java.util.Locale.ROOT):"rowan");return;}
        if(action.equals("list")){for(var d:plugin.merchants().all())plugin.send(p,T.t("merchant-command.waypoints", "<gold><id> <gray>• <id2> • <size> waypoints • <set> • <set2>", "id", d.id(), "id2", plugin.merchants().status(d.id()), "size", d.route().size(), "set", (d.spawn()==null?"spawn missing":"spawn set"), "set2", (d.shop()==null?"store missing":"store set")));return;}
        String id=args.length>2?args[2].toLowerCase(java.util.Locale.ROOT):"";
        if(plugin.merchants().get(id)==null){help(p);return;}
        switch(action){
            case "spawn","shop","point","end"->plugin.merchants().setPoint(p,id,action,p.getLocation().clone());
            case "undo","routeclear"->plugin.merchants().undo(p,id,action.equals("routeclear"));
            case "walk"->plugin.merchants().walk(id,p);
            case "despawn"->plugin.merchants().disable(p,id);
            case "edit"->MerchantEditor.open(plugin,p,id);
            case "wand"->{var leftovers=p.getInventory().addItem(plugin.merchants().wand(id));plugin.merchants().showTrail(p,id);plugin.send(p,leftovers.isEmpty()?"<gold>Right-click ground to mark the trail; left-click to undo. Finish with /cq merchant end "+id+".":"<yellow>Make room for the route wand and try again.");}
            default->help(p);
        }
    }
    private void help(Player p){plugin.send(p,T.t("merchant-command.cq-merchant-list-cq-merchant", "<white>/cq merchant list\n<white>/cq merchant test [id|stop] <gray>• temporary walk and trade preview\n<white>/cq merchant spawn|point|shop|end <id> <gray>• record where you stand\n<white>/cq merchant wand <id> <gray>• click a route\n<white>/cq merchant undo|routeclear <id>\n<white>/cq merchant walk|despawn|edit <id>\n<gray>Set spawn, use the wand to mark a trail, then end while facing the store direction. Maximum gap: 32 blocks."));}
}
