package com.cquests.gui;

import com.cquests.CQuestsPlugin;
import com.cquests.command.QuestsCommand;
import com.cquests.data.*;
import com.cquests.dialogue.MailDialog;
import com.cquests.model.*;
import com.cquests.npc.NpcRegistry;
import com.cquests.progression.Progression;
import com.cquests.quest.*;
import net.kyori.adventure.inventory.Book;
import org.bukkit.entity.Player;
import org.junit.jupiter.api.Test;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

class QuestJournalTest {
    record Screen(String title,List<String> lines,List<MailDialog.Button> buttons) {}
    record Context(CQuestsPlugin plugin,Player player,PlayerData data,QuestManager manager,Quest quest,List<Screen> screens) {
        void run(String... args){QuestJournal.command(plugin,player,args);}
        Screen screen(){return screens.getLast();}
    }
    private void check(java.util.function.Consumer<Context> test){
        var plugin=mock(CQuestsPlugin.class);var player=mock(Player.class);var data=new PlayerData(UUID.randomUUID());data.setMenuMode("book");
        var manager=mock(QuestManager.class);var registry=mock(QuestRegistry.class);var npcs=mock(NpcRegistry.class);var progression=mock(Progression.class);
        var directions=mock(Directions.class);var tracker=mock(Tracker.class);var quest=mock(Quest.class);
        var objective=new Objective(ObjectiveType.HARVEST,null,10,"","wheat");
        when(quest.id()).thenReturn("welcome");when(quest.name()).thenReturn("A helping hand");when(quest.level()).thenReturn(1);when(quest.giver()).thenReturn("stephan");when(quest.turnIn()).thenReturn("stephan");when(quest.objectives()).thenReturn(List.of(objective));
        data.start(new ActiveQuest("welcome",1,1));
        when(player.hasPermission("quests.use")).thenReturn(true);when(plugin.questManager()).thenReturn(manager);when(manager.data(player)).thenReturn(data);
        when(manager.fill(anyString(),eq(player))).thenAnswer(i->i.getArgument(0));
        when(plugin.quests()).thenReturn(registry);when(registry.get("welcome")).thenReturn(quest);when(manager.nextStoryQuest(data)).thenReturn(quest);when(manager.activeQuests(data)).thenReturn(List.of(quest));
        when(plugin.npcs()).thenReturn(npcs);when(npcs.name("stephan")).thenReturn("Stephan");when(plugin.progression()).thenReturn(progression);when(progression.level(data)).thenReturn(5);when(progression.canTake(data,1)).thenReturn(true);
        when(plugin.tracker()).thenReturn(tracker);when(plugin.directions()).thenReturn(directions);when(manager.objectiveLabel(objective)).thenReturn("Harvest wheat");
        var screens=new ArrayList<Screen>();
        try(var dialog=mockStatic(MailDialog.class)){
            dialog.when(()->MailDialog.open(any(),any(),anyString(),anyList(),anyList(),anyBoolean())).thenAnswer(i->{screens.add(new Screen(i.getArgument(2),List.copyOf(i.getArgument(3)),List.copyOf(i.getArgument(4))));return true;});
            test.accept(new Context(plugin,player,data,manager,quest,screens));
            verify(player,never()).openBook(any(Book.class));verify(manager,never()).accept(any(),any());verify(manager,never()).complete(any(),any());
        }
    }
    @Test void defaultCommandOpensHomeEvenWithSavedBookPreference(){check(c->{
        new QuestsCommand(c.plugin()).onCommand(c.player(),null,"quests",new String[0]);
        assertEquals("Quest home",c.screen().title());assertEquals("book",c.data().menuMode("menu"));
        assertTrue(c.screen().buttons().stream().anyMatch(b->b.label().equals("What should I do?")));
        assertFalse(c.screen().buttons().stream().anyMatch(b->b.label().toLowerCase().contains("book")));
    });}
    @Test void taskHasPlainNextStepAndBothBackPaths(){check(c->{
        c.run("journal","quest","welcome");assertTrue(c.screen().lines().toString().contains("Next: Harvest wheat (0/10)"));
        assertTrue(c.screen().buttons().stream().anyMatch(b->b.command().equals("/quests journal quests")));
        assertTrue(c.screen().buttons().stream().anyMatch(b->b.command().equals("/quests journal")));
        assertEquals(1,c.data().active().size());assertEquals(0,c.data().completedCount());
    });}
    @Test void futureQuestCannotBeOpenedByForgingAButtonCommand(){check(c->{
        var future=mock(Quest.class);when(future.id()).thenReturn("future");when(c.plugin().quests().get("future")).thenReturn(future);
        c.run("journal","quest","future");assertEquals("Quest home",c.screen().title());
    });}
    @Test void levelGateExplainsWhatToDoWithoutOfferingAcceptance(){check(c->{
        c.data().remove("welcome");when(c.quest().level()).thenReturn(100);
        c.run("journal","story");assertTrue(c.screen().lines().toString().contains("Reach Wayfarer level 100 first"));
        assertTrue(c.screen().buttons().stream().noneMatch(b->b.command().contains("accept")||b.command().contains("guide")));
    });}
    @Test void settingsAndFarmHelpAlwaysReturnHome(){check(c->{
        c.run("journal","settings");assertEquals("Quest settings",c.screen().title());assertEquals(3,c.screen().buttons().size());
        c.run("journal","tracker");verify(c.plugin().tracker()).toggle(c.player());assertEquals("Quest settings",c.screen().title());
        c.run("journal","farm");assertEquals("Farming & tools",c.screen().title());assertTrue(c.screen().buttons().stream().anyMatch(b->b.label().equals("Back to quest home")));
    });}
    @Test void showingDirectionsIsIdempotentAndDoesNotToggleThemOff(){check(c->{
        c.run("journal","guide","welcome");verify(c.plugin().directions()).toggle(c.player());
        when(c.plugin().directions().enabled(c.player())).thenReturn(true);c.run("journal","guide","welcome");
        verify(c.plugin().directions(),times(1)).toggle(c.player());verify(c.plugin().tracker(),times(2)).track(c.player(),"welcome");
    });}
    @Test void directMenuEntryStillRequiresJournalPermission(){check(c->{
        when(c.player().hasPermission("quests.use")).thenReturn(false);QuestJournal.open(c.plugin(),c.player());assertTrue(c.screens().isEmpty());
    });}
}
