# CQuests 1.6.1

NPC speech now keeps sentence typing separate from its reading pause. Clicking during the pause no longer makes the following sentence appear instantly.

- While a sentence is typing, click the NPC to reveal the rest of that sentence.
- While a completed sentence is being held for reading, click to start the next sentence immediately. It still types letter by letter.
- After the final sentence, click to open the choices immediately, without waiting for the reading pause or continue animation.
- With no clicks, every sentence types and keeps the configured reading time. Existing character speed and reading-pause settings are retained.

This shared playback applies to quest NPCs, merchant introductions and companion speech that use the overhead dialogue controller. Player progress, NPC definitions and optional Gemini settings are unchanged. Stop the server and replace the JAR, keeping the existing CQuests data folder.
