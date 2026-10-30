package com.cquests.quest;

import com.cquests.Settings;
import com.cquests.model.NpcDef;
import com.cquests.model.Objective;
import com.cquests.model.ObjectiveType;
import com.cquests.model.Quest;
import com.cquests.model.QuestCategory;
import com.cquests.model.Reward;
import com.cquests.model.RewardItem;
import com.cquests.model.TargetMatcher;
import com.cquests.npc.NpcRegistry;
import com.cquests.util.Text;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Random;
import java.util.Set;
import java.util.logging.Logger;

/**
 * Builds side quests and the daily pool from the templates in generator.yml.
 * The output is deterministic for a given seed, so a quest id always means the same quest
 * as long as the templates are not reordered.
 */
public final class QuestGenerator {

    private record Target(String spec, int minLevel, int base, int max, String singular, String plural) {
    }

    private record TypeTemplate(ObjectiveType type, int weight, List<String> names, List<String> flavor, List<Target> targets) {
    }

    private record Tier(int maxLevel, long minMoney, long maxMoney, List<RewardItem> items) {
    }

    private final YamlConfiguration cfg;
    private final Settings settings;
    private final NpcRegistry npcs;
    private final Logger log;
    private final List<TypeTemplate> types = new ArrayList<>();
    private final List<Tier> tiers = new ArrayList<>();
    private final List<String> thanks;
    private final List<String> places;

    public QuestGenerator(YamlConfiguration cfg, Settings settings, NpcRegistry npcs, Logger log) {
        this.cfg = cfg;
        this.settings = settings;
        this.npcs = npcs;
        this.log = log;
        this.thanks = cfg.getStringList("thanks").isEmpty()
                ? List.of("Thank you, {player}. That helps more than you know.")
                : cfg.getStringList("thanks");
        this.places = cfg.getStringList("places");
        loadTypes();
        loadTiers();
    }

    private void loadTypes() {
        ConfigurationSection root = cfg.getConfigurationSection("types");
        if (root == null) {
            return;
        }
        for (String key : root.getKeys(false)) {
            ObjectiveType type;
            try {
                type = ObjectiveType.valueOf(key.toUpperCase(Locale.ROOT));
            } catch (IllegalArgumentException e) {
                log.warning("generator.yml: unknown type " + key);
                continue;
            }
            if (type == ObjectiveType.TALK) {
                continue;
            }
            ConfigurationSection s = root.getConfigurationSection(key);
            if (s == null) {
                continue;
            }
            List<Target> targets = new ArrayList<>();
            for (String line : s.getStringList("targets")) {
                String[] p = line.split("\\|");
                if (p.length < 6) {
                    log.warning("generator.yml: bad target line '" + line + "' (need SPEC | min-level | base | max | singular | plural)");
                    continue;
                }
                try {
                    targets.add(new Target(p[0].trim(), Integer.parseInt(p[1].trim()), Integer.parseInt(p[2].trim()),
                            Integer.parseInt(p[3].trim()), p[4].trim(), p[5].trim()));
                } catch (NumberFormatException e) {
                    log.warning("generator.yml: bad number in '" + line + "'");
                }
            }
            if (!targets.isEmpty()) {
                types.add(new TypeTemplate(type, Math.max(1, s.getInt("weight", 10)),
                        s.getStringList("names"), s.getStringList("flavor"), targets));
            }
        }
    }

    private void loadTiers() {
        for (String line : cfg.getStringList("reward-tiers")) {
            String[] p = line.split("\\|");
            if (p.length < 3) {
                continue;
            }
            List<RewardItem> items = new ArrayList<>();
            if (p.length > 3) {
                for (String item : p[3].split(",")) {
                    RewardItem parsed = QuestRegistry.parseItem(item);
                    if (parsed != null) {
                        items.add(parsed);
                    }
                }
            }
            tiers.add(new Tier(Integer.parseInt(p[0].trim()), Long.parseLong(p[1].trim()), Long.parseLong(p[2].trim()), items));
        }
        if (tiers.isEmpty()) {
            tiers.add(new Tier(Integer.MAX_VALUE, 250, 1000, List.of()));
        }
    }

    public int perNpc() {
        return Math.max(0, cfg.getInt("side-quests-per-npc", 10_000));
    }

    /**
     * Side quest number {@code index} (1-based) of an NPC. Built on demand from the seed, so a million
     * quests cost no memory until someone actually takes one. Later quests have higher levels,
     * bigger amounts and more objectives.
     */
    public Quest side(NpcDef npc, int index, List<String> requires) {
        int i = index - 1;
        Random rnd = new Random(seed() * 31 + npc.id().hashCode() * 1_000_003L + i);
        double progress = Math.min(1.0, i / (double) Math.max(1, cfg.getInt("ramp-quests", 500)));
        int level = Math.min(99, npc.level() + i / Math.max(1, cfg.getInt("level-up-every", 100)));
        double p2 = lerp(cfg.getDoubleList("two-objective-chance"), 0.15, 0.5, progress);
        double p3 = lerp(cfg.getDoubleList("three-objective-chance"), 0.0, 0.25, progress);
        double roll = rnd.nextDouble();
        int count = roll < p3 ? 3 : roll < p3 + p2 ? 2 : 1;
        double ramp = 0.8 + 0.5 * progress;
        return build("side_" + npc.id() + "_" + index, QuestCategory.SIDE, index, npc, level, count, ramp, requires,
                rnd, cfg.getDouble("item-chance", 0.6), -1);
    }

    public List<Quest> dailyPool() {
        List<Quest> out = new ArrayList<>();
        NpcDef dailyNpc = npcs.get(settings.dailyNpc);
        if (dailyNpc == null) {
            return out;
        }
        int pool = Math.max(0, cfg.getInt("daily.pool-size", 60));
        int level = cfg.getInt("daily.level", 45);
        int objectives = Math.max(1, cfg.getInt("daily.objectives", 2));
        for (int i = 0; i < pool; i++) {
            Random rnd = new Random(seed() * 17 + 99_991L * i);
            Quest quest = build("daily_" + (i + 1), QuestCategory.DAILY, i, dailyNpc, level, objectives,
                    1.0, List.of(), rnd, 0, settings.dailyMoney);
            if (quest != null) {
                out.add(quest);
            }
        }
        return out;
    }

    private long seed() {
        return cfg.getLong("seed", 1337);
    }

    private static double lerp(List<Double> range, double from, double to, double t) {
        if (range.size() == 2) {
            from = range.get(0);
            to = range.get(1);
        }
        return from + (to - from) * t;
    }

    private Quest build(String id, QuestCategory category, int order, NpcDef giver, int level, int objectiveCount,
                        double ramp, List<String> requires, Random rnd, double itemChance, long fixedMoney) {
        List<Objective> objectives = new ArrayList<>();
        Set<String> usedSpecs = new HashSet<>();
        TypeTemplate firstType = null;
        Target firstTarget = null;
        int firstAmount = 0;
        // How much work the quest is: each objective counts as its share of that target's top amount,
        // weighted up for targets that only unlock at higher levels. Rewards follow this number.
        double effort = 0;
        for (int attempt = 0; attempt < 20 && objectives.size() < objectiveCount; attempt++) {
            TypeTemplate type = pickType(rnd, level);
            if (type == null) {
                break;
            }
            List<Target> allowed = type.targets().stream().filter(t -> t.minLevel() <= level).toList();
            Target target = allowed.get(rnd.nextInt(allowed.size()));
            if (!usedSpecs.add(type.type() + ":" + target.spec())) {
                continue;
            }
            double scale = objectiveCount == 1 ? 1.0 : 0.7;
            int amount = amountFor(target, level, ramp * scale, rnd);
            String npc = type.type() == ObjectiveType.DELIVER ? giver.id() : "";
            objectives.add(new Objective(type.type(), TargetMatcher.parse(target.spec(), settings.groups), amount, npc,
                    amount == 1 ? target.singular() : target.plural()));
            effort += amount / (double) Math.max(1, target.max()) * (1 + target.minLevel() / 100.0);
            if (firstType == null) {
                firstType = type;
                firstTarget = target;
                firstAmount = amount;
            }
        }
        if (objectives.isEmpty()) {
            return null;
        }

        String name = fill(pick(firstType.names(), rnd, "{Singular} Task"), firstTarget, firstAmount, giver);
        if (!places.isEmpty() && rnd.nextDouble() < cfg.getDouble("place-chance", 0.6)) {
            name = name + " " + places.get(rnd.nextInt(places.size()));
        }
        String description = fill(pick(firstType.flavor(), rnd, "{npc} needs a hand."), firstTarget, firstAmount, giver);

        Tier tier = tierFor(level);
        long money;
        List<RewardItem> items = new ArrayList<>();
        if (fixedMoney >= 0) {
            money = fixedMoney;
        } else {
            // Bigger, longer quests pay more: the tier's range is spread over effort, then each extra objective adds 35%.
            double share = Math.min(1.0, effort / 1.5);
            double raw = tier.minMoney() + share * (tier.maxMoney() - tier.minMoney());
            raw *= (1 + 0.35 * (objectives.size() - 1)) * (0.92 + rnd.nextDouble() * 0.16);
            money = Math.max(50, Math.round(raw / 50.0) * 50);
            if (!tier.items().isEmpty() && rnd.nextDouble() < itemChance * Math.min(1.5, 0.5 + effort)) {
                items.add(tier.items().get(rnd.nextInt(tier.items().size())));
                if (effort > 1.5) {
                    RewardItem bonus = tier.items().get(rnd.nextInt(tier.items().size()));
                    RewardItem first = items.get(0);
                    if (bonus.material() == first.material()) {
                        items.set(0, new RewardItem(first.material(), first.amount() + bonus.amount()));
                    } else {
                        items.add(bonus);
                    }
                }
            }
        }
        List<String> complete = List.of(pick(thanks, rnd, "Thank you."));
        return new Quest(id, name, level, category, order, giver.id(), giver.id(), requires, List.copyOf(objectives),
                description, List.of(description), complete, new Reward(money, List.copyOf(items), List.of(), 0), false, 0);
    }

    private TypeTemplate pickType(Random rnd, int level) {
        int total = 0;
        for (TypeTemplate type : types) {
            if (hasTarget(type, level)) {
                total += type.weight();
            }
        }
        if (total == 0) {
            return null;
        }
        int roll = rnd.nextInt(total);
        for (TypeTemplate type : types) {
            if (!hasTarget(type, level)) {
                continue;
            }
            roll -= type.weight();
            if (roll < 0) {
                return type;
            }
        }
        return null;
    }

    private static boolean hasTarget(TypeTemplate type, int level) {
        for (Target target : type.targets()) {
            if (target.minLevel() <= level) {
                return true;
            }
        }
        return false;
    }

    private static int amountFor(Target target, int level, double ramp, Random rnd) {
        double progress = target.minLevel() >= 99 ? 1 : Math.max(0, Math.min(1, (level - target.minLevel()) / (99.0 - target.minLevel())));
        double raw = (target.base() + (target.max() - target.base()) * progress) * ramp * (0.85 + rnd.nextDouble() * 0.3);
        int amount = (int) Math.max(1, Math.round(raw));
        if (amount > 100) {
            amount = Math.round(amount / 10f) * 10;
        } else if (amount > 20) {
            amount = Math.round(amount / 5f) * 5;
        }
        return Math.max(1, Math.min(amount, Math.max(target.max(), 1)));
    }

    private Tier tierFor(int level) {
        for (Tier tier : tiers) {
            if (level <= tier.maxLevel()) {
                return tier;
            }
        }
        return tiers.get(tiers.size() - 1);
    }

    private String fill(String template, Target target, int amount, NpcDef npc) {
        return template
                .replace("{Singular}", Text.capitalize(target.singular()))
                .replace("{Plural}", Text.capitalize(target.plural()))
                .replace("{singular}", target.singular())
                .replace("{plural}", target.plural())
                .replace("{amount}", Integer.toString(amount))
                .replace("{npc}", npcs.mention(npc.id()));
    }

    private static String pick(List<String> list, Random rnd, String fallback) {
        return list.isEmpty() ? fallback : list.get(rnd.nextInt(list.size()));
    }
}
