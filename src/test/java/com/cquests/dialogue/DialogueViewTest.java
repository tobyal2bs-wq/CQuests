package com.cquests.dialogue;
import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;
class DialogueViewTest {
    @Test void longConversationsHaveBoundedPagesAndKeepAllWords() {
        String input = "A long conversation with B.O.B. ".repeat(50).strip();
        var pages = DialogueView.paginate(List.of("<white>" + input), 24, 10);
        assertTrue(pages.size() > 1);
        for (var page : pages) {
            assertTrue(page.size() <= 10);
            page.forEach(line -> assertTrue(line.length() <= 24));
        }
        assertEquals(input, String.join(" ", pages.stream().flatMap(List::stream).toList()));
    }
}
