# Native merchants and replyable mail

Stop the server, back up CQuests data, replace the JAR and retain the data folder. NPC locations, routes, exact trade templates, token balances, levels and quest progress remain in the existing files.

## Merchant window

All six merchants now use Minecraft's native villager trading window: offers on the left, two ingredient slots, an arrow and the result on the right. Select an offer and left-click its result to buy one trade. The window closes after a purchase; open it again to make another purchase. Shift-click and double-click bulk purchases are intentionally disabled.

Payments come from the player's real inventory, Vault balance and saved sunflower pouch. The displayed ingredients are locked previews; they are not items the player can take. Hover the result to see the full item, money and sunflower prices. Minecraft has only two ingredient slots, so additional combined currency costs appear in the tooltip. A sunflower stack icon is capped at 64, while the tooltip shows the full token price.

The server rechecks range, current offer revision, exact item metadata, wallet balance, money payment and reward capacity. Duplicate result packets cannot reuse one confirmation. Preview items are tagged and guarded against inventory movement, drops, creative clicks, closing, death and reconnecting.

The OP-only crouch editor, route wand, end-facing command and private merchant demo remain available. `/cq merchant edit <id>` edits item templates, money and sunflower prices. `/cq merchant test flora` opens a temporary private walk/preview without payment.

## Letters and replies

`/quest mail` opens the mailbox. Each letter shows its sender and saved delivery time in UTC. Selecting a letter opens a native dialogue on supported clients, with the message, **Read as a book**, **Write a reply**, and **Back to mailbox**. Older clients receive the compatible book view.

Delivery timestamps are recorded the first time an eligible letter is delivered/observed by this version. They are retained on rereads and restart. Previously installed letters have no historical delivery timestamp to recover; their first timestamp is recorded after upgrading.

The reply button opens a native text composer. On older clients, a suggested command provides the same function:

```text
/quest mail send first_welcome Your message here
/quest mail replies
```

The book view also has a reply link. No physical book, inventory paper or signed-book item is needed or consumed. Replies and answers stay in the player's private correspondence; the newest 40 entries are retained. A maximum of 800 characters is accepted per outgoing letter. Other villagers send authored acknowledgements; these can be customised using `reply:` on each letter in `letters.yml`, with `{player}` and `{sender}` placeholders.

Mail commands also support `open <letter-id>`, `book <letter-id>` and `compose <letter-id>`. Every operation checks that the letter is available in the player's own journey. Reading, replying and AI text never complete quests or grant currency, items, XP or permissions.

## B.O.B through Gemini

Gemini replies are disabled by default. No API request is made until all four requirements are satisfied:

1. Put the Gemini API key in the server process environment variable `CQUESTS_GEMINI_API_KEY`. Keep the key out of chat, the repository and the character file. Restart the server after changing its environment.
2. Set an available model ID in `plugins/CQuests/ai-mail.yml` under `model:`. The shipped value is blank so the operator chooses the model and its costs.
3. Replace `plugins/CQuests/bob-character.txt` with B.O.B's character notes, emotional reactions, history and example letters. Remove the `CQUESTS_CHARACTER_PENDING` marker. Up to 16,000 characters are used.
4. Set `enabled: true` in `ai-mail.yml`, then `/cq reload` to reload model, character notes and settings.

The character file guides the model at request time; this does not train or fine-tune a new model. The character file and example letters still need to be supplied before B.O.B's voice can be prepared and assessed.

When a player replies to an available B.O.B letter, Google receives that letter, the player's recent conversation for that letter, their saved quest decisions and completed-quest count. General server chat and other players' mail are not sent. The composer explains this before sending. Keys are sent only in the HTTPS authentication header; requests use Google's fixed Gemini endpoint without redirects.

Generation runs off server/region threads, with two workers, a bounded queue, a request timeout, one pending request per player and a 30-second player cooldown. Defaults are 12 requests per player per UTC day and 100 per server per UTC day. Player limits and the server budget are saved across restarts. Failed requests can still consume quota; there are no automatic retries.

Replies are stored as plain text. They have no tool access and cannot execute chat commands, modify quests, pay rewards or create click actions. Rate limits and instruction prompts do not guarantee perfect character consistency; check the resulting letters after adding the real profile. Model availability, a valid key, Google account billing and actual generated quality require a live provider test.

Gemini API configuration reference: https://ai.google.dev/api/generate-content
