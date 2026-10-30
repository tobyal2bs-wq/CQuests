package com.cquests.model;

import org.bukkit.Material;

import java.util.ArrayList;
import java.util.EnumSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

/**
 * Matches entity/material names against a spec such as {@code ZOMBIE}, {@code COAL_ORE|DEEPSLATE_COAL_ORE},
 * {@code *_LOG}, {@code @LOGS} (a group from config.yml) or {@code ANY}.
 */
public final class TargetMatcher {

    public static final TargetMatcher ANY = new TargetMatcher("ANY", List.of(), true);

    private final String spec;
    private final List<Pattern> patterns;
    private final boolean any;
    private volatile Set<Material> materials;

    private TargetMatcher(String spec, List<Pattern> patterns, boolean any) {
        this.spec = spec;
        this.patterns = patterns;
        this.any = any;
    }

    public static TargetMatcher parse(String spec, Map<String, List<String>> groups) {
        String upper = spec.trim().toUpperCase(Locale.ROOT);
        if (upper.isEmpty() || upper.equals("ANY") || upper.equals("*")) {
            return ANY;
        }
        List<Pattern> patterns = new ArrayList<>();
        for (String part : upper.split("\\|")) {
            addPart(part.trim(), groups, patterns, 0);
        }
        return new TargetMatcher(upper, List.copyOf(patterns), false);
    }

    private static void addPart(String part, Map<String, List<String>> groups, List<Pattern> out, int depth) {
        if (part.isEmpty()) {
            return;
        }
        if (part.startsWith("@") && depth < 4) {
            List<String> members = groups.get(part.substring(1));
            if (members != null) {
                for (String member : members) {
                    addPart(member.trim().toUpperCase(Locale.ROOT), groups, out, depth + 1);
                }
            }
            return;
        }
        String regex = Pattern.quote(part).replace("*", "\\E.*\\Q");
        out.add(Pattern.compile(regex));
    }

    public boolean any() {
        return any;
    }

    public String spec() {
        return spec;
    }

    public boolean matches(String key) {
        if (any) {
            return true;
        }
        for (Pattern pattern : patterns) {
            if (pattern.matcher(key).matches()) {
                return true;
            }
        }
        return false;
    }

    /** Item materials this matcher accepts, used for deliveries. */
    public Set<Material> materials() {
        Set<Material> cached = materials;
        if (cached == null) {
            cached = EnumSet.noneOf(Material.class);
            for (Material material : Material.values()) {
                if (!material.isLegacy() && material.isItem() && matches(material.name())) {
                    cached.add(material);
                }
            }
            materials = cached;
        }
        return cached;
    }
}
