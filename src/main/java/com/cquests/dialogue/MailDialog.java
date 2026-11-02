package com.cquests.dialogue;

import com.cquests.CQuestsPlugin;
import com.cquests.util.Text;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.event.ClickEvent;
import org.bukkit.entity.Player;
import java.util.*;
import java.util.function.Consumer;

/** Optional native mail dialogue and reply input, isolated from the legacy server API. */
public final class MailDialog {
    private static final String ROOT="io.papermc.paper.registry.data.dialog.";
    public record Button(String label,String command){}
    private MailDialog(){}
    public static boolean open(CQuestsPlugin plugin,Player player,String title,List<String> lines,List<Button> buttons,boolean input){
        if(!NativeDialogue.available()||!com.cquests.util.Platform.supportsDialogs(player))return false;
        try{
            Class<?> base=Class.forName(ROOT+"DialogBase"),builder=Class.forName(ROOT+"DialogBase$Builder"),body=Class.forName(ROOT+"body.DialogBody"),action=Class.forName(ROOT+"action.DialogAction"),button=Class.forName(ROOT+"ActionButton"),type=Class.forName(ROOT+"type.DialogType"),multi=Class.forName(ROOT+"type.MultiActionType$Builder");
            Object b=base.getMethod("builder",Component.class).invoke(null,Component.text(title));
            builder.getMethod("body",List.class).invoke(b,List.of(body.getMethod("plainMessage",Component.class,int.class).invoke(null,Text.mm(String.join("\n\n",lines)),360)));
            builder.getMethod("canCloseWithEscape",boolean.class).invoke(b,true);
            if(input){
                var inputs=Class.forName(ROOT+"input.DialogInput");var textBuilder=Class.forName(ROOT+"input.TextDialogInput$Builder");
                Object field=inputs.getMethod("text",String.class,Component.class).invoke(null,"message",Component.text("Your message"));
                textBuilder.getMethod("maxLength",int.class).invoke(field,800);textBuilder.getMethod("width",int.class).invoke(field,300);
                builder.getMethod("inputs",List.class).invoke(b,List.of(textBuilder.getMethod("build").invoke(field)));
            }
            Object builtBase=builder.getMethod("build").invoke(b);var actions=new ArrayList<Object>();
            for(var value:buttons){Object click=value.command().contains("$(message)")?action.getMethod("commandTemplate",String.class).invoke(null,value.command()):action.getMethod("staticAction",ClickEvent.class).invoke(null,ClickEvent.runCommand(value.command()));actions.add(button.getMethod("create",Component.class,Component.class,int.class,action).invoke(null,Component.text(value.label()),null,300,click));}
            Object typeBuilder=type.getMethod("multiAction",List.class).invoke(null,actions);multi.getMethod("columns",int.class).invoke(typeBuilder,1);Object builtType=multi.getMethod("build").invoke(typeBuilder);
            Consumer<Object> setup=factory->{try{Object entry=Class.forName("io.papermc.paper.registry.RegistryBuilderFactory").getMethod("empty").invoke(factory);var entryType=Class.forName(ROOT+"DialogRegistryEntry$Builder");entryType.getMethod("base",base).invoke(entry,builtBase);entryType.getMethod("type",type).invoke(entry,builtType);}catch(ReflectiveOperationException e){throw new IllegalStateException(e);}};
            Object dialog=Class.forName("io.papermc.paper.dialog.Dialog").getMethod("create",Consumer.class).invoke(null,setup);
            player.getClass().getMethod("showDialog",Class.forName("net.kyori.adventure.dialog.DialogLike")).invoke(player,dialog);return true;
        }catch(ReflectiveOperationException|RuntimeException|LinkageError e){plugin.getLogger().warning("Mail dialogue unavailable; using compatible mail menu.");return false;}
    }
}
