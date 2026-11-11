"""Which bosses ship, by group. Every model module registers its bosses; a later module's version of an id
replaces an earlier one, and only the ids listed here are built."""
import importlib
import models

MODULES = ["v2_general", "v2_seasonal", "v2_chapters", "v2_legends", "v3_general", "v3_mythic", "v3_seasonal",
           "v4_normal", "v4_chapters", "v4_seasonal", "v5_normal", "v5_mythic", "v6_originals", "v7_bigs", "v8_pumpkins", "v9_minis", "v10_fixes", "v11_new", "v12_final", "v13_approved", "v14_studio", "v15_minis", "v16_pixel", "v17_sculpt", "v18_seasonal", "v20_mob"]

# the weekly rotation: the first 25 bosses, then the new ones drawn from the user's pictures
GENERAL = ["slagheart", "warlord_gruk", "grand_augur", "crimson_ronin", "thunderback", "gorehorn", "abyssal_eye", "overgrowth",
           "prism_sentinel", "tiki_warden", "broodmother", "tide_tyrant",
           "storm_herald", "pharaoh", "executioner", "ember_queen", "gravelord", "captain_brine", "keywarden", "bloodtusk", "king_gloop",
           "clockwork_colossus", "mossback", "old_wizard", "hollow_mage", "horned_brute", "rotting_giant", "dusk_scorpion",
           "grave_marshal", "mayor_grumble", "old_ironroot", "frost_yeti", "bog_orc", "millstone_monk", "moonwake_manta", "thorncoil_basilisk"]
MYTHIC = ["the_listener", "withered_tyrant", "the_unmaker"]
SEASONAL = {"winter": ["killer_claus", "frostbottom", "old_man_winter"], "summer": ["sunscorch", "admiral_pinchworth", "brain_freeze"],
            "spring": ["clucksworth", "killer_bunny", "cocoa_colossus"], "halloween": ["gourd_king", "headless_horseman", "hexmother"]}
CHAPTERS = ["brakka", "gate_shade", "oakheart", "gnome_brothers", "moss_spirit", "grubnose", "mudclub", "ugor"]
DECOR = ["decor_pumpkin_tall", "decor_pumpkin_flat", "decor_pumpkin_cube"]


def minis():
    import v9_minis, v12_final, v14_studio
    return list(v9_minis.MINIS)


def partners():
    import v12_final
    return list(v12_final.PARTNERS.values())


ALL = GENERAL + MYTHIC + [b for s in SEASONAL.values() for b in s] + CHAPTERS + DECOR


def builders():
    """id -> the function that builds it (the last module to define an id wins)."""
    for mod in MODULES:
        importlib.import_module(mod)
    by_id = {}
    # a later module wins, whatever order the modules happened to be imported in
    rank = {m: i for i, m in enumerate(MODULES)}
    for fn in sorted(models.MODELS, key=lambda f: rank.get(f.__module__, -1)):
        by_id[fn.__name__] = fn
    ids = ALL + minis() + partners()
    missing = [i for i in ids if i not in by_id]
    if missing:
        raise SystemExit("no model for " + ", ".join(missing))
    return {i: by_id[i] for i in ids}


def recipes():
    import v2_recipes, v4_recipes, v8_recipes, v9_minis, v11_new, v12_final, v14_studio, v18_seasonal
    spawn, death = dict(v2_recipes.SPAWN), dict(v2_recipes.DEATH)
    for r in (v4_recipes, v8_recipes, v9_minis, v11_new, v12_final):
        spawn.update(r.SPAWN)
        death.update(r.DEATH)
    return spawn, death
