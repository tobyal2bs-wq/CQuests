"""Display names. The first batch of names were all glued-together words (Slagheart, Sproutbeak, Thorncoil)
and "The X of the Y" titles, which the user found read like a generator wrote them. These are plain names a
person would give: short first names, nicknames and job titles, with short, plain titles under them.

Ids never change, so servers keep their settings and rewards. A server whose boss still carries the old name
or title (one nobody edited) gets the new one on the next start; a name an admin changed is left alone."""

NAMES = {
    # big bosses
    "slagheart": ("Magmus", "The Lava Golem"),
    "warlord_gruk": ("Warlord Gruk", "Piglin Boss of the Bastion"),
    "grand_augur": ("King Malrick", "Ruler of the Illagers"),
    "crimson_ronin": ("Akuma", "The Red Oni"),
    "thunderback": ("Big Bongo", "The Storm Gorilla"),
    "gorehorn": ("Gorehorn", "Minotaur of the Pit"),
    "abyssal_eye": ("Mama Gulp", "The Deep Sea Angler"),
    "overgrowth": ("Rusty", "The Jungle Golem"),
    "prism_sentinel": ("Gemma", "The Crystal Golem"),
    "tiki_warden": ("Big Tiki", "Idol of the Island"),
    "broodmother": ("Widow Mae", "Queen of the Spiders"),
    "tide_tyrant": ("King Crabby", "Ruler of the Reef"),
    "storm_herald": ("Bjorn", "The Storm Ram"),
    "pharaoh": ("Pharaoh Ankhamun", "Back From the Tomb"),
    "executioner": ("The Executioner", "Axe of the Mansion"),
    "ember_queen": ("Big Bertha", "The Living Furnace"),
    "gravelord": ("Mister Bones", "The Gravedigger"),
    "gate_shade": ("Grimsby", "Nothing Passes Without the Key"),
    "captain_brine": ("Captain Brine", "Captain of the Drowned"),
    "keywarden": ("Old Jangles", "Keeper of the Five Keys"),
    "bloodtusk": ("Hamhock", "The War Boar"),
    "king_gloop": ("King Gloop", "King of the Swamp"),
    "clockwork_colossus": ("Tick-Tock", "The Clockwork Giant"),
    "mossback": ("Boulder", "The Walking Hill"),
    "old_wizard": ("Wizard Aldo", "Older Than the Mountains"),
    "hollow_mage": ("Hollow Hank", "Nothing Under the Hat"),
    "cinder_hollow": ("Smoky Hank", "His Hat Is Still Burning"),
    "rime_hollow": ("Chilly Hank", "Snow on His Hat"),
    "bramble_hollow": ("Mossy Hank", "Mushrooms on His Hat"),
    "horned_brute": ("Gorrak", "Brute of the Mountain Pass"),
    "rotting_giant": ("Big Gus", "Too Big to Stay Buried"),
    "dusk_scorpion": ("Stinger", "The Desert Scorpion"),
    "grave_marshal": ("Marshal Graves", "Keeps the Dead in Line"),
    "mayor_grumble": ("Mayor Grumble", "Taxes Are Due"),
    "old_ironroot": ("Grandpa Oak", "The Oldest Tree"),
    "frost_yeti": ("Yuki", "The Cave Yeti"),
    "bog_orc": ("Grok", "The Swamp Bully"),
    "millstone_monk": ("Brother Miller", "Keeper of the Old Mill"),
    "moonwake_manta": ("Luna", "The Moon Manta"),
    "thorncoil_basilisk": ("Viper", "The Thorn Serpent"),
    "rootmaw": ("Big Root", "The Giant Mandrake"),
    "brewgut": ("Bruno", "The Tavern Ogre"),
    # seasonal
    "frostbottom": ("Frosty", "The Angry Snowman"),
    "sunscorch": ("Sunny", "Melting on Holiday"),
    "cocoa_colossus": ("Eggbert", "The Chocolate Egg"),
    "gourd_king": ("Jack", "King of the Pumpkins"),
    "hexmother": ("Granny Morwen", "The Swamp Witch"),
    # chapter bosses
    "moss_spirit": ("Old Moss", "Two Faces in the Stone"),
    "grubnose": ("Grub", "The Bridge Troll"),
    "mudclub": ("Mudd", "The River Troll"),
    "ugor": ("Ugor", "The Last Brute"),
    # minis
    "bark_ape": ("Coco", "The Jungle Thief"),
    "old_blindman": ("Hermit Ezra", "He Hears Every Step"),
    "king_oldbeard": ("King Albert", "Ruler of One Village"),
    "gilded_mimic": ("Goldie", "Too Shiny to Trust"),
    "mossling": ("Twig", "Hatched From a Bush"),
    "apple_crab": ("Pinchy", "The Apple Crab"),
    "moss_imp": ("Sprig", "Small and Very Old"),
    "angry_goose": ("Gertrude", "The Angry Goose"),
    "goblin_king": ("King Grizzle", "His Crown Is Too Big"),
    "snapjaw": ("Chomper", "The Hungry Flower"),
    "cap_brothers": ("Toad", "The Grumpy Mushroom"),
    "puffneck": ("Dandy", "Blows Away in the Wind"),
    "mallard": ("Sir Quacks", "Crosses Any Road"),
    "hay_golem": ("Scarecrow Sam", "Guards the Wheat"),
    "mossy_turtle": ("Shelby", "Slow and Stubborn"),
    "bogwart": ("Warty", "Waits in the Reeds"),
    "old_pip": ("Grandpa Pip", "The Gnome Elder"),
    "sproutbeak": ("Hedgey", "A Hedge With Legs"),
}

# titles a boss had under an earlier entry here, so servers still showing one get the new title
EARLIER_TITLES = {"gravelord": ["He Brings an Empty Sack"]}


def rename(id, name, title):
    """The new (name, title) for a boss, keeping the old name's colours and bold tags."""
    if id not in NAMES: return name, title
    new, sub = NAMES[id]
    if "<bold>" in name and "</bold>" in name:
        a, b = name.index("<bold>") + 6, name.index("</bold>")
        return name[:a] + new + name[b:], sub
    import re
    m = re.match(r"^((?:<[^>]+>)*)(.*?)((?:</[^>]+>)*)$", name)
    return (m.group(1) + new + m.group(3), sub) if m else (new, sub)
