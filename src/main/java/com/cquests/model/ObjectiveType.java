package com.cquests.model;

public enum ObjectiveType {
    KILL("Kill"),
    MINE("Mine"),
    HARVEST("Harvest"),
    PLACE("Place"),
    CRAFT("Craft"),
    SMELT("Smelt"),
    FISH("Catch"),
    BREED("Breed"),
    TAME("Tame"),
    SHEAR("Shear"),
    ENCHANT("Enchant"),
    CONSUME("Eat"),
    DELIVER("Bring"),
    TALK("Talk to"),
    FIND("Find");

    private final String verb;

    ObjectiveType(String verb) {
        this.verb = verb;
    }

    public String verb() {
        return verb;
    }

    /** Objectives that are completed by clicking an NPC rather than by a game event. */
    public boolean npcBound() {
        return this == DELIVER || this == TALK;
    }
}
