package com.cquests.adventure;

import com.cquests.CQuestsPlugin;
import com.cquests.data.PlayerData;
import com.cquests.data.PlayerStore;
import com.cquests.dialogue.MailDialog;
import com.cquests.quest.QuestManager;
import net.kyori.adventure.inventory.Book;
import org.bukkit.entity.Player;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.nio.file.*;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

class MailFlowTest {
    @TempDir Path folder;
    record Screen(String title,List<String> lines,List<MailDialog.Button> buttons,boolean input) {}
    @SuppressWarnings("unchecked")
    private void flow(java.util.function.BiConsumer<QuestMail,List<Screen>> check) throws Exception {
        Files.writeString(folder.resolve("letters.yml"),"""
                letters:
                  welcome:
                    sender: Stephan
                    subject: Welcome home
                    body: ['A letter for {player}.']
                    reply: 'See you soon, {player}.'
                  bob:
                    sender: B.O.B
                    subject: The old field
                    body: ['I found your marker.']
                  secret:
                    sender: Esme
                    subject: A secret
                    quest: locked_story
                    body: ['Not available yet.']
                """);
        var plugin=mock(CQuestsPlugin.class);var manager=mock(QuestManager.class);var store=mock(PlayerStore.class);
        var player=mock(Player.class);var data=new PlayerData(UUID.randomUUID());var gemini=mock(GeminiMail.class);
        when(plugin.getDataFolder()).thenReturn(folder.toFile());when(plugin.questManager()).thenReturn(manager);
        when(plugin.store()).thenReturn(store);when(plugin.gemini()).thenReturn(gemini);when(gemini.unavailable()).thenReturn("Disabled");
        when(manager.data(player)).thenReturn(data);when(player.getName()).thenReturn("Alex");when(player.getUniqueId()).thenReturn(data.uuid());
        var screens=new ArrayList<Screen>();
        try(var dialog=mockStatic(MailDialog.class)) {
            dialog.when(()->MailDialog.open(any(),any(),anyString(),anyList(),anyList(),anyBoolean())).thenAnswer(i->{screens.add(new Screen(i.getArgument(2),List.copyOf(i.getArgument(3)),List.copyOf(i.getArgument(4)),i.getArgument(5)));return true;});
            var mail=new QuestMail(plugin);
            // The callback uses this same player and ledger through command helpers below.
            currentPlayer=player;currentData=data;
            check.accept(mail,screens);
            verify(player,never()).openBook(any(Book.class));
        }
    }
    private Player currentPlayer;private PlayerData currentData;
    private void command(QuestMail mail,String... args){mail.command(currentPlayer,args);}

    @Test void inboxStartsInDialogueAndDoesNotExposeUnavailableLetters() throws Exception {
        flow((mail,screens)->{
            mail.open(currentPlayer);var screen=screens.getLast();assertEquals("Your mail",screen.title());
            assertTrue(screen.buttons().stream().anyMatch(b->b.command().equals("/quest mail open welcome")));
            assertFalse(screen.buttons().stream().anyMatch(b->b.command().contains("secret")||b.label().contains("book")));
            assertFalse(currentData.letterRead("welcome"));
        });
    }
    @Test void letterShowsSenderDateAndReplyWithoutBookDetour() throws Exception {
        flow((mail,screens)->{
            command(mail,"mail","open","welcome");var screen=screens.getLast();
            assertTrue(screen.lines().toString().contains("Stephan"));assertTrue(screen.lines().toString().contains("UTC"));assertTrue(screen.lines().toString().contains("Alex"));
            assertTrue(screen.buttons().stream().anyMatch(b->b.label().equals("Reply to Stephan")));
            assertTrue(currentData.letterRead("welcome"));
            command(mail,"mail","compose","welcome");assertTrue(screens.getLast().input());assertTrue(screens.getLast().buttons().stream().anyMatch(b->b.label().equals("Send")));
        });
    }
    @Test void sendingShowsAnswerAndHistoryInDialogues() throws Exception {
        flow((mail,screens)->{
            command(mail,"mail","send","welcome","Thank you!");
            assertEquals(2,currentData.mailThread().size());assertTrue(screens.getLast().lines().toString().contains("See you soon, Alex."));
            command(mail,"mail","replies");assertEquals("Sent letters & replies",screens.getLast().title());
            assertTrue(screens.getLast().buttons().stream().anyMatch(b->b.label().startsWith("To Stephan")));
        });
    }
    @Test void disabledBobHasNoReplyButtonAndForgedLockedMailDoesNotOpen() throws Exception {
        flow((mail,screens)->{
            command(mail,"mail","open","secret");assertTrue(screens.isEmpty());
            command(mail,"mail","open","bob");assertTrue(screens.getLast().buttons().stream().noneMatch(b->b.command().contains("compose")));
            command(mail,"mail","compose","bob");assertFalse(screens.getLast().input());
            assertTrue(currentData.mailThread().isEmpty());
        });
    }
}
