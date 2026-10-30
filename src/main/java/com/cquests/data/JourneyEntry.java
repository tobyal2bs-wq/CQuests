package com.cquests.data;

/** One finished story quest, remembered for the end-of-journey replay. */
public record JourneyEntry(String questId, long time, String world, double x, double y, double z) {

    String serialize() {
        return questId + ";" + time + ";" + world + ";" + x + ";" + y + ";" + z;
    }

    static JourneyEntry parse(String line) {
        String[] p = line.split(";");
        if (p.length < 6) {
            return null;
        }
        try {
            return new JourneyEntry(p[0], Long.parseLong(p[1]), p[2],
                    Double.parseDouble(p[3]), Double.parseDouble(p[4]), Double.parseDouble(p[5]));
        } catch (NumberFormatException e) {
            return null;
        }
    }
}
