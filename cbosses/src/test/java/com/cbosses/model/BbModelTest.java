package com.cbosses.model;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import org.junit.jupiter.api.Test;

import java.io.InputStreamReader;
import java.io.StringReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

/** Every built-in model goes out to Blockbench and comes back with the same blocks, bones and animations. */
class BbModelTest {
    @Test
    void everyModelSurvivesABlockbenchRoundTrip() throws Exception {
        JsonObject all;
        try (var in = getClass().getClassLoader().getResourceAsStream("models.json")) {
            all = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
        }
        for (var e : all.getAsJsonObject("models").entrySet()) {
            String id = e.getKey();
            JsonObject m = e.getValue().getAsJsonObject();
            JsonObject rig = all.getAsJsonObject("rigs").getAsJsonObject(m.get("rig").getAsString());
            JsonObject saved = JsonParser.parseString(BbModel.toBlockbench(id, m, rig).toString()).getAsJsonObject();
            JsonObject back = BbModel.toModel(id, saved, m, w -> { throw new AssertionError(w); });
            assertEquals(cubes(m), cubes(back), id + ": cubes changed on the way through Blockbench");
            assertEquals(m.getAsJsonArray("bones").size(), back.getAsJsonArray("bones").size(), id + ": bones");
            if (m.has("anims")) for (var a : m.getAsJsonObject("anims").entrySet()) {
                JsonObject was = a.getValue().getAsJsonObject(), now = back.getAsJsonObject("anims").getAsJsonObject(a.getKey());
                assertTrue(now != null, id + ": lost animation " + a.getKey());
                if (was.has("hit")) assertEquals(was.get("hit").getAsFloat(), now.get("hit").getAsFloat(), 1e-4, id + " " + a.getKey() + ": hit");
                for (var b : was.getAsJsonObject("bones").entrySet()) {
                    if (!now.getAsJsonObject("bones").has(b.getKey())) continue;   // keys on bones the model does not have
                    for (var ch : b.getValue().getAsJsonObject().entrySet()) {
                        var x = ch.getValue().getAsJsonArray();
                        var y = now.getAsJsonObject("bones").getAsJsonObject(b.getKey()).getAsJsonArray(ch.getKey());
                        assertEquals(x.size(), y.size(), id + " " + a.getKey() + " " + b.getKey());
                        for (int k = 0; k < x.size(); k++) for (int q = 0; q < 3; q++)
                            assertEquals(x.get(k).getAsJsonArray().get(1).getAsJsonArray().get(q).getAsFloat(),
                                    y.get(k).getAsJsonArray().get(1).getAsJsonArray().get(q).getAsFloat(), 1e-3, id + " " + a.getKey() + " " + b.getKey());
                    }
                }
            }
            JsonObject root = new JsonObject();
            root.add("rigs", all.getAsJsonObject("rigs"));
            JsonObject one = new JsonObject();
            one.add(id, back);
            root.add("models", one);
            assertTrue(ModelRig.load(new StringReader(root.toString())).containsKey(id), id + ": the plugin cannot load the imported model");
        }
    }

    private static List<String> cubes(JsonObject m) {
        List<String> out = new ArrayList<>();
        for (JsonElement e : m.getAsJsonArray("cubes")) {
            JsonObject c = e.getAsJsonObject();
            StringBuilder s = new StringBuilder(c.get("b").getAsString() + "/" + c.get("k").getAsString() + "/" + c.has("l") + "/" + c.get("g"));
            for (String k : new String[]{"f", "t", "r", "o"}) if (c.has(k))
                for (int i = 0; i < 3; i++) s.append(String.format(java.util.Locale.ROOT, "/%.3f", c.getAsJsonArray(k).get(i).getAsFloat()));
            out.add(s.toString());
        }
        Collections.sort(out);
        return out;
    }
}
