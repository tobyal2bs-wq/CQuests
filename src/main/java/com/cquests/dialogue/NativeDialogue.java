package com.cquests.dialogue;

import com.cquests.CQuestsPlugin;
import com.cquests.util.Text;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.event.ClickEvent;
import org.bukkit.entity.Player;
import java.util.List;
import java.util.function.Consumer;

/** Isolated capability bridge: no new dialog classes are linked on an older server. */
public final class NativeDialogue {
    private static final String ROOT = "io.papermc.paper.registry.data.dialog.";
    private NativeDialogue() {}
    public static boolean available() {
        try { Class.forName("io.papermc.paper.dialog.Dialog"); return true; }
        catch (ClassNotFoundException | LinkageError e) { return false; }
    }
    public static boolean open(CQuestsPlugin plugin, Player player, Component title, List<String> text, String label, String token) {
        if (!available()) return false;
        try {
            Class<?> dialog = Class.forName("io.papermc.paper.dialog.Dialog");
            Class<?> base = Class.forName(ROOT+"DialogBase"), baseBuilder = Class.forName(ROOT+"DialogBase$Builder");
            Class<?> body = Class.forName(ROOT+"body.DialogBody");
            Class<?> action = Class.forName(ROOT+"action.DialogAction"), button = Class.forName(ROOT+"ActionButton");
            Class<?> type = Class.forName(ROOT+"type.DialogType"), multi = Class.forName(ROOT+"type.MultiActionType$Builder");
            Object baseB = base.getMethod("builder", Component.class).invoke(null,title);
            Object message = body.getMethod("plainMessage", Component.class).invoke(null,Text.mm(String.join("\n\n",text)));
            baseBuilder.getMethod("body",List.class).invoke(baseB,List.of(message));
            baseBuilder.getMethod("canCloseWithEscape",boolean.class).invoke(baseB,true);
            Object builtBase = baseBuilder.getMethod("build").invoke(baseB);
            Object exit = button.getMethod("create",Component.class,Component.class,int.class,action)
                    .invoke(null,Component.text("Return to the world"),null,200,null);
            List<Object> buttons;
            if (token != null) {
                Object click = action.getMethod("staticAction",ClickEvent.class).invoke(null,ClickEvent.runCommand("/quests respond "+token));
                Object accept = button.getMethod("create",Component.class,Component.class,int.class,action)
                        .invoke(null,Text.mm("<gold><bold>"+Text.escape(label)),Component.text("Your choice is checked again before it is applied."),220,click);
                buttons=List.of(accept);
            } else buttons=List.of(exit);
            Object typeB = type.getMethod("multiAction",List.class).invoke(null,buttons);
            multi.getMethod("columns",int.class).invoke(typeB,1);
            if(token!=null)multi.getMethod("exitAction",button).invoke(typeB,exit);
            Object builtType=multi.getMethod("build").invoke(typeB);
            Consumer<Object> setup = factory -> {
                try {
                    Object builder=Class.forName("io.papermc.paper.registry.RegistryBuilderFactory").getMethod("empty").invoke(factory);
                    Class<?> b=Class.forName(ROOT+"DialogRegistryEntry$Builder");
                    b.getMethod("base",base).invoke(builder,builtBase);
                    b.getMethod("type",type).invoke(builder,builtType);
                } catch (ReflectiveOperationException e) { throw new IllegalStateException(e); }
            };
            Object built=dialog.getMethod("create",Consumer.class).invoke(null,setup);
            Class<?> like=Class.forName("net.kyori.adventure.dialog.DialogLike");
            player.getClass().getMethod("showDialog",like).invoke(player,built);
            return true;
        } catch (ReflectiveOperationException | RuntimeException | LinkageError e) {
            plugin.getLogger().warning("Native dialog unavailable on this build; using the compatible conversation menu: "+e+"; cause="+e.getCause());
            return false;
        }
    }
}
