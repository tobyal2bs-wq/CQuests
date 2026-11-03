# Chapters 6 to 10 for CQuests 1.7.0 and 1.8.0. Each chapter has twenty villagers; the tenth sends you into a
# private boss fight (bosses.yml). Run:  python3 tools/story/chapters_6_10.py src/main/resources
# It rewrites the block between the "# >>> chapters 6-10" markers in npcs.yml and quests.yml, so it
# is safe to run again. No quest asks for wheat.
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chapters_6_10_extra import EXTRA

q = json.dumps

CHAPTERS = {
    6: "The Iron Tusk",
    7: "Tides of the Drowned",
    8: "The Ember Court",
    9: "The Bone Choir",
    10: "The Listener Below",
}

# id, name, profession, skin, title, intro, quest name, objectives, offer, description, complete, idle
R = {6: [], 7: [], 8: [], 9: [], 10: []}
def row(ch, *a): R[ch].append(a)

# ------------------------------------------------------------------ 6: The Iron Tusk
row(6, "pip_scout", "Pip Tallow", "CARTOGRAPHER", "PLAINS", "the Road Scout",
    ["Pip Tallow! Scout, runner, professional optimist.", "The Wanderers are walking home to Aldmere, but raiders block the old road."],
    "The Road Home", ["PLACE COBBLESTONE|STONE_BRICKS|GRAVEL|DIRT_PATH 64 road blocks"],
    ["Lay some road for the caravan.", "Cobble, stone bricks, gravel. Anything a cart won't sink into."],
    "Lay 64 blocks of road for the Wanderers' caravan home.",
    ["Look at that! A road you could roll a pumpkin down."],
    "Left, right, left, right. The road always wins.")
row(6, "jd", "J.D.", "MASON", "PLAINS", "the Gatewright",
    ["Name's J.D. Just the letters. Long story.", "I'm rebuilding the gate of Aldmere, stone by stone."],
    "Gatewright", ["MINE STONE|COBBLESTONE|DEEPSLATE|COBBLED_DEEPSLATE 192 stone"],
    ["A gate needs stone. A lot of stone.", "Three stacks should do it. Probably."],
    "Mine stone for {npc:jd}'s new city gate.",
    ["She's going to be beautiful. The gate, I mean."],
    "J.D. stands for Just Done. Ask me when the gate's finished.")
row(6, "lampwright", "Dr. Ember", "CLERIC", "DESERT", "Doctor of Lamps",
    ["Dr. Ember. Doctor of lamps. It's a real degree, I promise.", "The old streets are pitch dark, and the raiders love that."],
    "Lights of Aldmere", ["CRAFT LANTERN 16 lanterns"],
    ["Craft me sixteen lanterns.", "Iron nuggets and a torch each. Easy."],
    "Craft lanterns to light the streets of Aldmere for {npc:lampwright}.",
    ["The streets glow again. Lovely, isn't it?"],
    "A lamp is a small sun you can carry.")
row(6, "rook", "Rook", "WEAPONSMITH", "TAIGA", "Captain of the Guard",
    ["Rook. Captain of the new city guard.", "Which is me. I am the guard."],
    "Clear the Ruins", ["KILL ZOMBIE|SKELETON|SPIDER|CREEPER 40 monsters"],
    ["The ruins are crawling with monsters.", "Forty of them. Then we can move families in."],
    "Clear forty monsters from the ruins of Aldmere for {npc:rook}.",
    ["Safe streets. You should join the guard. Paid in bread."],
    "Halt! Oh, it's you. Carry on.")
row(6, "wilma", "Wilma", "LEATHERWORKER", "SAVANNA", "the Tanner",
    ["Wilma. Saddles, boots and very good bags.", "Families moving home need all three."],
    "Leather for Everyone", ["DELIVER LEATHER 32 leather"],
    ["Bring me leather.", "Thirty two pieces should outfit the first families."],
    "Bring leather to {npc:wilma} for the returning families.",
    ["Thirty two pairs of boots, coming up!"],
    "Good boots, good day. Simple as that.")
row(6, "clover", "Clover", "FARMER", "PLAINS", "the Stablehand",
    ["Clover. I run the new stables.", "Every courier in Aldmere needs a horse. I have zero horses."],
    "Stable Hands", ["TAME HORSE|DONKEY|MULE 3 horses"],
    ["Tame three horses for the stables.", "Keep getting back on. They give in eventually."],
    "Tame horses for {npc:clover}'s new stables.",
    ["Look at them! Already eating all my hay."],
    "A horse knows when you're scared. So be brave.")
row(6, "max", "M.A.X", "TOOLSMITH", "PLAINS", "B.O.B's Little Brother",
    ["BEEP. I AM M.A.X. MECHANICAL ASSISTANT, EXPERIMENTAL.", "MY BROTHER B.O.B SAYS YOU ARE TRUSTWORTHY.", "I NEED POWER."],
    "Power Up", ["MINE REDSTONE_ORE|DEEPSLATE_REDSTONE_ORE 24 redstone ore"],
    ["BRING ME REDSTONE. IT TICKLES.", "TWENTY FOUR ORE. BEEP."],
    "Mine redstone ore to power up {npc:max}.",
    ["POWER LEVELS: EXCELLENT. HAPPINESS: ALSO EXCELLENT. BEEP BOOP."],
    "BEEP. I HAVE TOUCHED GRASS. IT WAS AS DESCRIBED.")
row(6, "sully", "Sully", "BUTCHER", "SWAMP", "the Swineherd",
    ["Sully. Pigs. Mostly pigs.", "A city without bacon is just a very large camp."],
    "Pig Pen", ["BREED PIG|COW|CHICKEN 20 animals"],
    ["The farm needs animals. Breed twenty.", "Carrots for pigs, seeds for chickens."],
    "Breed animals to fill {npc:sully}'s farm.",
    ["Oink. That's pig for thank you."],
    "I named every pig. Don't ask about the names.")
row(6, "pemberly", "Lord Pemberly", "ARMORER", "PLAINS", "the Mayor",
    ["I am Lord Pemberly, mayor of Aldmere. Elected yesterday. By myself.", "The raiders who block the road answer to a beast. A Ravager in iron."],
    "Raiders on the Road", ["KILL PILLAGER|VINDICATOR 20 raiders"],
    ["Thin out the raiders first.", "Twenty of them. Then their beast will come looking for you."],
    "Drive off the raiders blocking the road for {npc:pemberly}.",
    ["The road is quieter. Too quiet. Their beast is angry now."],
    "A mayor's work is never done. Mostly it's signing things.")
row(6, "garrick", "Old Garrick", "WEAPONSMITH", "TAIGA", "the Beast Hunter",
    ["Garrick. I've hunted beasts for sixty years.", "Gorehorn, the Iron Tusk, wrecked my village when I was a boy.", "It will only come for one hunter at a time. Make it you."],
    "The Iron Tusk", ["KILL RAVAGER 1 Gorehorn the Iron Tusk"],
    ["Click me when you're ready and I'll call it.", "It hunts only you. Nobody else can be hurt, and it breaks nothing but your pride."],
    "Face Gorehorn, the Iron Tusk, in a fight called by {npc:garrick}.",
    ["Sixty years. Sixty years, and you did it in an afternoon.", "The road home is open. Aldmere will remember you."],
    "Every scar has a story. Most of mine are about that beast.")

# ------------------------------------------------------------------ 7: Tides of the Drowned
row(7, "marisol", "Marisol", "FISHERMAN", "BEACH", "the Harbourmaster",
    ["Marisol. I keep Aldmere's new harbour.", "Ships have stopped coming. The sea has turned against us."],
    "Silent Harbour", ["FISH ANY 15 catches"],
    ["Fish the harbour for me.", "If the fish are gone, something is very wrong."],
    "Fish the harbour to see what's left for {npc:marisol}.",
    ["The fish are fleeing inland. Something drives them."],
    "The tide always comes back. Usually.")
row(7, "hugh", "Hugh", "FISHERMAN", "RIVER", "the Ferryman",
    ["Hugh. I run the ferry across the Aldwater.", "No boat, no ferry. No ferry, no Hugh."],
    "Ferry Across", ["CRAFT *_BOAT 3 boats"],
    ["Craft me three boats.", "Any wood. I'm not picky, I'm a ferryman."],
    "Craft boats for {npc:hugh}'s ferry.",
    ["All aboard! Mind the drowned."],
    "The river doesn't care who you are. That's why I like it.")
row(7, "coral", "Coral", "CLERIC", "WARM_OCEAN", "the Reef Keeper",
    ["Coral. I tend the reef.", "Prismarine keeps the deep calm. We've run out."],
    "Reef Mending", ["DELIVER PRISMARINE_SHARD 24 prismarine shards"],
    ["Bring me prismarine shards.", "Guardians carry them. Mind the lasers."],
    "Bring prismarine shards to {npc:coral} to mend the reef.",
    ["The reef sings again. Can you hear it?"],
    "Coral grows a hand's width in a hundred years. Be patient with it.")
row(7, "kelpie", "Kelpie", "NITWIT", "OCEAN", "the Kelp Collector",
    ["Kelpie! I collect kelp. Do you collect anything?", "The drowned keep eating my kelp."],
    "Kelp Crisis", ["SMELT DRIED_KELP 32 dried kelp"],
    ["Dry me some kelp.", "Thirty two pieces. It's for a very important snack."],
    "Smelt dried kelp for {npc:kelpie}'s very important snack.",
    ["Crunchy. Salty. Perfect."],
    "Kelp is just a tree that went swimming.")
row(7, "tobias_net", "Tobias", "FISHERMAN", "BEACH", "the Netmaker",
    ["Tobias. I mend nets.", "Something cuts them every night. Something with a trident."],
    "Mending Nets", ["DELIVER STRING 32 string"],
    ["Bring string for the nets.", "Spiders have plenty."],
    "Bring string to {npc:tobias_net} to mend the harbour nets.",
    ["Strong nets. Let them try cutting these."],
    "A net is mostly holes held together by hope.")
row(7, "dex_diver", "Dex", "LEATHERWORKER", "OCEAN", "the Diver",
    ["Dex. I dive.", "Down there I saw a palace. Drowned guards. A crown."],
    "Down Below", ["KILL DROWNED 25 drowned"],
    ["Clear the drowned from the shallows.", "Twenty five. Then we can see the palace."],
    "Clear the drowned guarding the shallows for {npc:dex_diver}.",
    ["The water's clear. The palace is real, {player}. And someone is sitting on the throne."],
    "Hold your breath. Longer. Longer.")
row(7, "seraphine", "Seraphine", "LIBRARIAN", "BEACH", "the Tide Reader",
    ["Seraphine. I read the tides like books.", "The tides speak of a queen who drowned with her fleet."],
    "Turtle Watch", ["BREED TURTLE 4 turtles"],
    ["Turtles always find their way home.", "Breed four and they'll show us the palace."],
    "Breed turtles for {npc:seraphine} so they can lead the way.",
    ["The little ones swim straight for the palace. As I read."],
    "High tide, low tide, story tide.")
row(7, "conch", "Admiral Conch", "ARMORER", "BEACH", "of the Lost Fleet",
    ["Admiral Conch. Of a fleet that no longer exists.", "Brinewyn was my queen. The sea took her, and kept her."],
    "Ship Shape", ["DELIVER IRON_INGOT 32 iron ingots", "DELIVER @LOGS 64 logs"],
    ["Help me rebuild one ship.", "Iron and wood. Then we sail for the palace."],
    "Bring iron and logs to {npc:conch} to rebuild a ship.",
    ["She floats. Barely. That's all we need."],
    "Sailors never die. They just smell like it.")
row(7, "nerissa", "Nerissa", "CLERIC", "OCEAN", "the Sea Witch",
    ["Nerissa. Don't call me a witch. Fine, call me a witch.", "To breathe at the palace you'll need my brews."],
    "Water Breathing", ["CRAFT CONDUIT 1 conduit"],
    ["A conduit, {player}. Nautilus shells and a heart of the sea.", "Then the sea will let you breathe."],
    "Craft a conduit for {npc:nerissa}'s protection spell.",
    ["The sea will let you breathe now. Whether it lets you leave is up to you."],
    "Bubbles are just the ocean laughing.")
row(7, "brine", "Brine", "FISHERMAN", "WARM_OCEAN", "the Queen's Herald",
    ["I am Brine, herald of Queen Brinewyn.", "Her Majesty will receive you. One challenger. Only one."],
    "Queen of the Drowned", ["KILL DROWNED 1 Queen Brinewyn"],
    ["Click me when you are ready to be received.", "The Queen fights only you. No one else can be harmed, and nothing will be broken."],
    "Face Queen Brinewyn, summoned by {npc:brine}.",
    ["Her Majesty is at peace. The tides are ours again.", "Thank you. I have waited a hundred years to say that."],
    "The Queen will see you now. Probably.")

# ------------------------------------------------------------------ 8: The Ember Court
row(8, "cinder", "Cinder", "ARMORER", "NETHER_WASTES", "the Gatekeeper",
    ["Cinder. I guard the gate to the Ember Court.", "The court burns hotter every day. Soon it'll spill into the overworld."],
    "Heat Shield", ["CRAFT FIRE_CHARGE 16 fire charges"],
    ["Fight fire with fire.", "Craft sixteen fire charges. We'll need them."],
    "Craft fire charges for {npc:cinder}.",
    ["Now we're cooking. Literally."],
    "Mind your eyebrows.")
row(8, "magmus", "Magmus", "TOOLSMITH", "BASALT_DELTAS", "the Basalt Breaker",
    ["Magmus. I break rocks that don't want to be broken.", "The court walls are basalt. Thick, thick basalt."],
    "Basalt Walls", ["MINE BASALT|BLACKSTONE 128 basalt"],
    ["Break through the outer wall.", "Basalt or blackstone. Two stacks."],
    "Mine through the Ember Court's outer walls for {npc:magmus}.",
    ["A hole! A beautiful, hot hole."],
    "Rocks are just very slow lava.")
row(8, "ash", "Ash", "LIBRARIAN", "SOUL_SAND_VALLEY", "the Soul Scribe",
    ["Ash. I write down what the souls whisper.", "They whisper about a matriarch made of fire."],
    "Soul Whispers", ["MINE SOUL_SAND|SOUL_SOIL 64 soul sand"],
    ["Bring me soul sand to listen through.", "The more we have, the more they tell."],
    "Mine soul sand so {npc:ash} can hear the souls.",
    ["They say her name is Pyra. They say she was a cook once. Odd."],
    "Shh. They're talking about you.")
row(8, "brimstone", "Brimstone", "WEAPONSMITH", "CRIMSON_FOREST", "the Hoglin Tamer",
    ["Brimstone. Hoglins respect me. Mostly.", "Their herds block the court road."],
    "Hoglin Herd", ["KILL HOGLIN 15 hoglins"],
    ["Thin the herd.", "Fifteen hoglins. Bring me a chop or two."],
    "Thin the hoglin herd on the court road for {npc:brimstone}.",
    ["The road's open. Dinner's on me."],
    "Never look a hoglin in the eye. It's rude.")
row(8, "quartzine", "Quartzine", "MASON", "NETHER_WASTES", "the Quartz Carver",
    ["Quartzine. I carve.", "The court's doors are sealed with quartz runes."],
    "Quartz Runes", ["MINE NETHER_QUARTZ_ORE 48 quartz ore"],
    ["Bring me quartz to carve a key.", "Forty eight ore."],
    "Mine quartz ore for {npc:quartzine}'s rune key.",
    ["The key is carved. The doors will open for you."],
    "Every rune is a word. Every word is a door.")
row(8, "goldtooth", "Goldtooth", "NITWIT", "NETHER_WASTES", "the Piglin Trader",
    ["Goldtooth. I trade with piglins. They trade with my teeth.", "The court's guards love gold. Let's bribe them."],
    "Golden Bribe", ["DELIVER GOLD_INGOT 32 gold ingots"],
    ["Gold, {player}. Shiny, shiny gold.", "Thirty two ingots."],
    "Bring gold to {npc:goldtooth} to bribe the court's guards.",
    ["They took it. They'll look the other way. Mostly."],
    "Gold makes friends. Bad friends, but friends.")
row(8, "warpwick", "Warpwick", "CARTOGRAPHER", "WARPED_FOREST", "the Warped Wanderer",
    ["Warpwick. I map the warped woods. Nobody else will.", "Endermen guard the shortcut to the court."],
    "Warped Shortcut", ["KILL ENDERMAN 15 endermen"],
    ["Clear the shortcut.", "Fifteen endermen. Don't look them in the eye either."],
    "Clear the endermen from the warped shortcut for {npc:warpwick}.",
    ["Shortcut's clear. My maps finally make sense."],
    "Left at the blue tree. Every tree is blue.")
row(8, "fennel", "Fennel", "CLERIC", "BASALT_DELTAS", "the Fire Brewer",
    ["Fennel. I brew things that don't burn.", "You'll want fire resistance in the court."],
    "Fireproof", ["DELIVER MAGMA_CREAM 12 magma cream", "DELIVER BLAZE_ROD 8 blaze rods"],
    ["Bring magma cream and blaze rods.", "I'll brew you something that laughs at lava."],
    "Bring ingredients to {npc:fennel} for fire resistance.",
    ["Drink up. Then go and be very, very brave."],
    "Bubble, bubble, nether trouble.")
row(8, "ignatius", "Sir Ignatius", "ARMORER", "NETHER_WASTES", "the Court Knight",
    ["Sir Ignatius. Knight of the Ember Court, once.", "The court's blazes must fall before the Matriarch shows herself."],
    "Court Guards", ["KILL BLAZE 25 blazes"],
    ["Defeat her guards.", "Twenty five blazes."],
    "Defeat the Ember Court's blaze guards for {npc:ignatius}.",
    ["She's seen you now. She's coming. Go to the herald."],
    "Honour burns brightest in the dark.")
row(8, "emberly", "Emberly", "NITWIT", "NETHER_WASTES", "the Court Herald",
    ["I am Emberly, herald of the Matriarch.", "Pyra will duel one challenger. You."],
    "The Ember Matriarch", ["KILL BLAZE 1 Pyra the Ember Matriarch"],
    ["Click me when you are ready.", "She fights only you. Her flames light nothing but you."],
    "Face Pyra, the Ember Matriarch, called by {npc:emberly}.",
    ["The court cools. For the first time in an age, it is merely warm.", "Thank you, champion."],
    "Hot, isn't it? It's always hot.")

# ------------------------------------------------------------------ 9: The Bone Choir
row(9, "hollis", "Hollis", "CLERIC", "DARK_FOREST", "the Gravekeeper",
    ["Hollis. I keep the graves quiet.", "Lately they sing. Every night. A choir of bones."],
    "Night Shift", ["KILL SKELETON 40 skeletons"],
    ["Quiet the singers.", "Forty skeletons."],
    "Quiet the singing skeletons for {npc:hollis}.",
    ["Quieter. But the song comes from somewhere deeper."],
    "The dead should rest. That's the rule.")
row(9, "bonnie", "Bonnie", "BUTCHER", "PLAINS", "the Bonemeal Baker",
    ["Bonnie! I make bonemeal. For flowers!", "With all these skeletons, I've never had so much."],
    "Bone Harvest", ["DELIVER BONE 64 bones"],
    ["Bring me bones.", "A stack. I'll grow a garden over the graves."],
    "Bring bones to {npc:bonnie} for a garden over the graves.",
    ["Flowers over every grave. Better already."],
    "Every bone wants to be a flower, deep down.")
row(9, "requiem", "Requiem", "LIBRARIAN", "DARK_FOREST", "the Choir Scholar",
    ["Requiem. I study music. Even the bad kind.", "The choir sings a hymn from the old kingdom."],
    "Sheet Music", ["CRAFT JUKEBOX 1 jukebox", "CRAFT NOTE_BLOCK 8 note blocks"],
    ["Build me something to play it back.", "A jukebox and eight note blocks."],
    "Craft a jukebox and note blocks for {npc:requiem}.",
    ["Listen. It's a lullaby. For a knight who never slept."],
    "Every song ends. Except that one.")
row(9, "tallow", "Tallow", "NITWIT", "SWAMP", "the Candlemaker",
    ["Tallow. Candles.", "The dead hate light. Let's give them a lot."],
    "Candle Vigil", ["CRAFT CANDLE 16 candles"],
    ["Make candles.", "Sixteen. One for every grave row."],
    "Craft candles for {npc:tallow}'s vigil.",
    ["The graveyard glows. They sing softer now."],
    "A candle is a promise to the dark.")
row(9, "grimsby", "Grimsby", "TOOLSMITH", "DARK_FOREST", "the Crypt Digger",
    ["Grimsby. I dig crypts. Badly.", "The choir sings from a crypt below the old chapel."],
    "Crypt Door", ["MINE DEEPSLATE|COBBLED_DEEPSLATE|TUFF 128 deepslate"],
    ["Dig down with me.", "Deepslate. Lots of it."],
    "Dig through deepslate to the crypt for {npc:grimsby}.",
    ["There's the door. Old iron. Older than old."],
    "Dig twice, cry once.")
row(9, "wren_bone", "Wren", "SHEPHERD", "PLAINS", "the Wolf Whisperer",
    ["Wren. My wolves can smell the dead.", "They'll guide you through the crypt."],
    "Pack Leader", ["TAME WOLF 4 wolves"],
    ["Tame four wolves.", "Bones work. You have plenty."],
    "Tame wolves to guide you through the crypt for {npc:wren_bone}.",
    ["Good dogs. The best dogs."],
    "Who's a good wolf? All of them.")
row(9, "morrow", "Morrow", "ARMORER", "DARK_FOREST", "the Crypt Smith",
    ["Morrow. I forge for the dead's enemies.", "Smite. You'll want smite."],
    "Holy Edge", ["ENCHANT ANY 8 enchantments"],
    ["Enchant your gear.", "Eight enchantments. The dead fear magic."],
    "Enchant your gear for the crypt with {npc:morrow}'s help.",
    ["Shining. The dead will hate it."],
    "Steel remembers every swing.")
row(9, "vesper", "Vesper", "CLERIC", "DARK_FOREST", "the Night Nun",
    ["Vesper. I pray at night, when it matters.", "The choir's soldiers are wither skeletons, from the old fortress guard."],
    "The Choir's Guard", ["KILL WITHER_SKELETON 20 wither skeletons"],
    ["Defeat the choir's guard.", "Twenty wither skeletons."],
    "Defeat the Bone Choir's guard for {npc:vesper}.",
    ["Only their conductor is left. Sir Mortis."],
    "Pray, then swing. In that order.")
row(9, "sexton", "Sexton", "NITWIT", "DARK_FOREST", "the Bell Ringer",
    ["Sexton. I ring the funeral bell.", "Mortis will wake when he hears it. Then he'll want you."],
    "Funeral Bell", ["DELIVER GOLD_BLOCK 2 gold blocks", "DELIVER IRON_BLOCK 4 iron blocks"],
    ["A bell needs metal.", "Two gold blocks, four iron blocks."],
    "Bring metal to {npc:sexton} to cast the funeral bell.",
    ["The bell is cast. When you're ready, go to the herald."],
    "Dong. Sorry, habit.")
row(9, "mortimer", "Mortimer", "LIBRARIAN", "DARK_FOREST", "the Choir Herald",
    ["I am Mortimer, herald of the Bone Choir.", "Sir Mortis conducts. He will duel you alone."],
    "The Bone Choir", ["KILL WITHER_SKELETON 1 Sir Mortis"],
    ["Click me when you're ready.", "He fights only you, and nothing will be broken but bones."],
    "Face Sir Mortis, conductor of the Bone Choir, called by {npc:mortimer}.",
    ["The song has ended. He finally sleeps.", "The crypt is silent, {player}. Thank you."],
    "Shh. The choir is resting.")

# ------------------------------------------------------------------ 10: The Listener Below
row(10, "echo", "Echo", "LIBRARIAN", "DEEP_DARK", "the Sculk Scholar",
    ["Echo. ...Echo. Sorry, joke.", "Something listens under Aldmere. It heard the bell."],
    "Sculk Samples", ["MINE SCULK|SCULK_VEIN 64 sculk"],
    ["Bring me sculk to study.", "Quietly. Very quietly."],
    "Mine sculk for {npc:echo} to study what listens below.",
    ["It's not one creature. It's the Listener. It remembers the Hollow."],
    "Don't make a sound. ...Too late.")
row(10, "whisper", "Whisper", "NITWIT", "DEEP_DARK", "the Quiet One",
    ["...", "(Whisper writes on a scrap of paper: wool muffles footsteps.)"],
    "Soft Steps", ["CRAFT *_CARPET 32 carpets"],
    ["(Make carpets. Lots of carpets.)", "(Thirty two. Please be quiet about it.)"],
    "Craft carpets so you can walk softly, as {npc:whisper} suggests.",
    ["(Whisper gives a silent thumbs up.)"],
    "...")
row(10, "gloam", "Gloam", "TOOLSMITH", "DEEP_DARK", "the Deepwright",
    ["Gloam. I build in the deep.", "We need light the Listener can't hear."],
    "Silent Light", ["CRAFT SEA_LANTERN|GLOWSTONE|SHROOMLIGHT 16 lights"],
    ["Make lights. The quiet kind.", "Sea lanterns, glowstone or shroomlights."],
    "Craft silent lights for {npc:gloam}'s path into the deep.",
    ["Bright, and not a sound. Perfect."],
    "Light is loud, if you listen.")
row(10, "anvara", "Anvara", "WEAPONSMITH", "DEEP_DARK", "the Deep Warden",
    ["Anvara. I guard the way down.", "Ancient cities lie below. Full of things that hear you breathe."],
    "Ancient Halls", ["KILL ZOMBIE|SKELETON|CREEPER|SPIDER 50 deep monsters"],
    ["Clear the halls.", "Fifty of them."],
    "Clear the ancient halls for {npc:anvara}.",
    ["The halls are clear. Now it's just you and it."],
    "Breathe slowly. It's listening.")
row(10, "oriel", "Oriel", "CLERIC", "LUSH_CAVES", "the Cave Gardener",
    ["Oriel. I grow things where the sun never shines.", "Glow berries calm the Listener. Mostly."],
    "Glow Garden", ["DELIVER GLOW_BERRIES 32 glow berries"],
    ["Bring me glow berries.", "Thirty two."],
    "Bring glow berries to {npc:oriel} to calm the deep.",
    ["The cave glows soft and green. The Listener stirs, but slower."],
    "Even the dark needs a garden.")
row(10, "flint_deep", "Flint", "MASON", "DEEP_DARK", "the Echo Miner",
    ["Flint. I mine echo shards.", "With enough shards, we can talk back to it."],
    "Echo Shards", ["DELIVER ECHO_SHARD 8 echo shards"],
    ["Bring echo shards from the ancient cities.", "Eight of them."],
    "Bring echo shards to {npc:flint_deep}.",
    ["Listen. The shards hum its name."],
    "Every echo is a question.")
row(10, "tamsin", "Tamsin", "CARTOGRAPHER", "DEEP_DARK", "the Last Mapmaker",
    ["Tamsin. Gwen's apprentice. And Penny's. And everyone's.", "I'm mapping the way to the Listener's hall."],
    "Deep Map", ["CRAFT RECOVERY_COMPASS 1 recovery compass"],
    ["Craft a recovery compass.", "If you fall down there, it'll bring you home."],
    "Craft a recovery compass for {npc:tamsin}'s map.",
    ["Now you can always find your way back."],
    "A map is a promise that someone came back.")
row(10, "hush", "Brother Hush", "CLERIC", "DEEP_DARK", "the Silent Monk",
    ["(Brother Hush bows and points at a sign: wool for the walls.)", "(The sign continues: the Listener cannot hear through wool.)"],
    "Wool Walls", ["DELIVER @WOOL 64 wool"],
    ["(He holds up the sign again, and taps the word wool twice.)", "(Sixty four, written very small at the bottom.)"],
    "Bring wool to {npc:hush} to line the walls of the deep chapel.",
    ["(Brother Hush smiles, very quietly.)"],
    "(Brother Hush nods.)")
row(10, "stephan_elder", "Elder Stephan", "LIBRARIAN", "PLAINS", "Keeper of the Road",
    ["Remember me? Stephan. A bit older. A bit wiser.", "You began this road with me. It ends below Aldmere."],
    "One Last Favour", ["DELIVER GOLDEN_APPLE 4 golden apples", "DELIVER TOTEM_OF_UNDYING 1 totem of undying"],
    ["Take what you need for the end.", "Bring me apples and a totem. I'll bless them."],
    "Bring golden apples and a totem to {npc:stephan_elder} for the last journey.",
    ["Blessed. Go on, {player}. The Wanderers are with you."],
    "Every road ends somewhere. Ours ends with you.")
row(10, "aldis_elder", "Mother Aldis", "NITWIT", "DARK_FOREST", "the Oracle",
    ["Child. You came back.", "The Listener is the last piece of the Hollow. It cannot be killed by many. Only by one."],
    "Ears of the Hollow", ["KILL WARDEN 1 The Listener Below"],
    ["Click me when you are ready.", "It hunts only you. It breaks nothing, and nobody else can be hurt."],
    "Face the Listener Below, the last of the Hollow, called by {npc:aldis_elder}.",
    ["It is over. Truly over. Listen... nothing.", "Aldmere is free, {player}. Rest now. You have earned it."],
    "Shhh. Listen. Nothing at all. Beautiful.")

SKIN = {"PLAINS":"PLAINS","DESERT":"DESERT","SAVANNA":"SAVANNA","SWAMP":"SWAMP","TAIGA":"TAIGA","BEACH":"PLAINS",
        "RIVER":"PLAINS","OCEAN":"PLAINS","WARM_OCEAN":"JUNGLE","NETHER_WASTES":"SAVANNA","BASALT_DELTAS":"SAVANNA",
        "SOUL_SAND_VALLEY":"SAVANNA","CRIMSON_FOREST":"SAVANNA","WARPED_FOREST":"SWAMP","DARK_FOREST":"TAIGA",
        "DEEP_DARK":"TAIGA","LUSH_CAVES":"JUNGLE"}
TOP_ITEMS = ["DIAMOND 4", "NETHERITE_SCRAP 1", "GOLDEN_APPLE 3", "EXPERIENCE_BOTTLE 48", "EMERALD_BLOCK 2", "DIAMOND_BLOCK 1"]
BOSS_ITEMS = {6: ["NETHERITE_INGOT 1", "DIAMOND 8"], 7: ["HEART_OF_THE_SEA 1", "TRIDENT 1"], 8: ["NETHERITE_INGOT 1", "BLAZE_ROD 16"],
              9: ["NETHERITE_INGOT 2", "GOLDEN_APPLE 6"], 10: ["NETHERITE_INGOT 3", "DIAMOND_BLOCK 4"]}
MINI_BOSSES = {"ironjaw_hunter", "frostpaw_keeper", "enforcer_hunter", "cantor_hunter", "wind_hunter"}
MINI_ITEMS = {6: ["DIAMOND 4", "IRON_BLOCK 4"], 7: ["DIAMOND 4", "PRISMARINE_CRYSTALS 16"], 8: ["DIAMOND 5", "GOLD_BLOCK 4"],
              9: ["DIAMOND 6", "EXPERIENCE_BOTTLE 32"], 10: ["DIAMOND 8", "ECHO_SHARD 4"]}
SKINNED = {"pemberly": "default", "conch": "default", "ignatius": "default", "stephan_elder": "default"}
BABY = {"pip_scout", "kelpie"}

def lst(lines, indent):
    pad = " " * indent
    return "".join(f"{pad}- {q(x)}\n" for x in lines)

def build():
    npcs, quests = [], []
    prev = "story_aldric"
    order = 101
    for ch in sorted(R):
        # The original nine, the ten from 1.8.0, then the boss villager last.
        rows = R[ch][:-1] + EXTRA[ch] + [R[ch][-1]]
        assert len(rows) == 20, (ch, len(rows))
        for j, r in enumerate(rows):
            (id, name, prof, skin, title, intro, qname, objs, offer, desc, complete, idle) = r
            level = 100 + (ch - 6) * 20 + j
            n = f"  {id}:\n    name: {q(name)}\n    title: {q(title)}\n    profession: {prof}\n    skin: {SKIN.get(skin, 'PLAINS')}\n"
            n += f"    level: {level}\n    act: 2\n    chapter: {ch}\n    personal: true\n"
            if id in BABY: n += "    baby: true\n"
            if id in SKINNED: n += f"    player-skin: {q(SKINNED[id])}\n"
            n += "    intro:\n" + lst(intro, 6) + "    idle:\n" + lst([idle], 6)
            npcs.append(n)
            complete = list(complete)
            last = j == len(rows) - 1
            if not last and not objs[-1].startswith("TALK"):
                complete.append("Go and see {npc:%s} next. They could use you." % rows[j + 1][0])
            boss = last
            mini = id in MINI_BOSSES
            money = 10000 if boss else 6000 if mini else int(round((2800 + (ch - 6) * 400 + j * 60) / 50.0)) * 50
            items = BOSS_ITEMS[ch] if boss else MINI_ITEMS[ch] if mini else [TOP_ITEMS[(ch + j) % len(TOP_ITEMS)]]
            qid = "story_" + id
            s = f"  {qid}:\n    name: {q(qname)}\n    level: {level}\n    order: {order}\n    giver: {q(id)}\n    chapter: {ch}\n"
            if boss or mini: s += "    big: true\n"
            s += f"    requires: [{prev}]\n    objectives:\n" + lst(objs, 6) + f"    description: {q(desc)}\n"
            s += "    offer:\n" + lst(offer, 6) + "    complete:\n" + lst(complete, 6)
            s += f"    rewards:\n      money: {money}\n      items:\n" + lst(items, 8)
            quests.append(s)
            prev = qid
            order += 1
    chapters = "".join(f"  {c}: {q(n)}\n" for c, n in CHAPTERS.items())
    return "".join(npcs), "".join(quests), chapters

def splice(path, section_header, block):
    text = open(path, encoding="utf-8").read()
    begin, end = "# >>> chapters 6-10 (tools/story/chapters_6_10.py)\n", "# <<< chapters 6-10\n"
    text = re.sub(re.escape(begin) + ".*?" + re.escape(end), "", text, flags=re.S)
    if not text.endswith("\n"): text += "\n"
    open(path, "w", encoding="utf-8").write(text + begin + block + end)

if __name__ == "__main__":
    out = sys.argv[1]
    npcs, quests, chapters = build()
    ids = [r[0] for ch in R for r in R[ch]] + [r[0] for ch in EXTRA for r in EXTRA[ch]]
    assert len(set(ids)) == 100
    splice(out + "/npcs.yml", "npcs:", npcs)
    splice(out + "/quests.yml", "quests:", quests)
    # chapter names go into the chapters: map at the top of quests.yml
    text = open(out + "/quests.yml", encoding="utf-8").read()
    text = re.sub(r'(  5: "The King Wakes"\n)(?:  (?:6|7|8|9|10): .*\n)*', lambda m: m.group(1) + chapters, text, count=1)
    open(out + "/quests.yml", "w", encoding="utf-8").write(text)
    print("ok", len(ids), "villagers")
