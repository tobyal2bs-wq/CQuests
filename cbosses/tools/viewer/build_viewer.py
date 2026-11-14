"""Builds the CBosses 3D viewer (docs/viewer.html) from the template, the models and bosses.yml.
Run after gen_models.py: python3 tools/viewer/build_viewer.py [out.html]"""
import json, os, re, sys
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(HERE, "..", "models"))
import anims, palette, v2_legends, v2_recipes as recipes  # noqa: F401  (registers rigs and texts)

models = json.load(open(os.path.join(ROOT, "src/main/resources/models.json")))
bosses = yaml.safe_load(open(os.path.join(ROOT, "src/main/resources/bosses.yml")))["bosses"]
THEME = {"soul": "#4fe0ff", "fire": "#ff8a1a", "frost": "#bfe9ff", "nature": "#7bd66a", "gold": "#ffc53d", "water": "#3aa6ff", "storm": "#d6ecff",
         "earth": "#a07850", "blood": "#e0303a", "toxic": "#8cff4a", "void": "#a05cff", "witch": "#c45cff", "sand": "#e6d08a", "bone": "#efe7cf",
         "sculk": "#2fd6d6", "wither": "#5a1020", "dragon": "#d14bff", "holiday": "#ff3b3b", "candy": "#ff8fc8", "pumpkin": "#ff9a1a", "feather": "#ffffff", "iron": "#c8c8c8", "wind": "#9fe7dc"}

def plain(mm):
    return re.sub(r"<[^>]+>", "", mm).strip()

def grad(mm, fallback):
    cols = re.findall(r"#[0-9a-fA-F]{6}", mm)
    return (cols[0], cols[-1]) if cols else (fallback, fallback)

out = []
for id, b in bosses.items():
    c1, c2 = grad(b["name"], THEME.get(b["theme"], "#ffb347"))
    kind = "mini" if b.get("kind") == "mini" else "chapter" if b.get("chapter") else "seasonal" if b.get("season") else "legend" if id in ("withered_tyrant", "ender_wyrm", "gale_sovereign", "the_listener", "the_unmaker") else "world"
    out.append({"id": id, "name": plain(b["name"]), "c1": c1, "c2": c2, "title": b.get("title", ""), "entity": b["entity"], "health": b["health"],
                "season": b.get("season", ""), "chapter": b.get("chapter", 0), "kind": kind, "bar": b.get("bar", "RED"), "abilities": b["abilities"],
                "color": THEME.get(b["theme"], c2), "theme": b["theme"], "movement": b.get("movement", "walk"), "description": b.get("description", ""),
                "spawnText": recipes.SPAWN_TEXT.get(id, ""), "deathText": recipes.DEATH_TEXT.get(id, "")})
# the decor props (spawned as scenery with /cb decor): shown in their own group, idle only
for id in [k for k in models["models"] if k.startswith("decor_")]:
    out.append({"id": id, "name": id[6:].replace("_", " ").title(), "c1": "#ffb347", "c2": "#ff7a00", "title": "Decor prop", "entity": "ARMOR_STAND",
                "health": 0, "season": "", "chapter": 0, "kind": "decor", "bar": "YELLOW", "abilities": [], "color": "#ff9a2a", "theme": "harvest",
                "movement": "still", "description": "Scenery that pulls faces. It cycles through every carved face it has.", "spawnText": "", "deathText": ""})
data = {"bosses": out, "models": models["models"], "rigs": models["rigs"], "palette": {k: list(v) for k, v in palette.P.items()}}

html = open(os.path.join(HERE, "template.html")).read()
html = html.replace("/*DATA*/", "const DATA = " + json.dumps(data, separators=(",", ":")) + ";")

def sub(old, new, count=1):
    global html
    assert old in html, old[:80]
    html = html.replace(old, new, count)

sub("<title>CQuests World Bosses</title>", "<title>CBosses Boss Viewer</title>")
sub("<h1>CQuests World Bosses</h1>", "<h1>CBosses</h1>")
html = re.sub(r"<header>\s*<h1>CBosses</h1>\s*<p>.*?</p>", "<header>\n    <h1>CBosses</h1>\n    <p>Every boss in the plugin as it is built in game: block models with their own attacks, entrance and death. "
              "Drag to turn the camera, scroll or pinch to zoom. Pick a boss, then press Entrance, Death or any attack. Flying bosses flap, the egg really hatches, "
              "and deaths shatter into shards. The browser draws rough stand-ins for the block textures; in game every piece is a real Minecraft block.</p>", html, flags=re.S)
if "<h1>CBosses</h1>\n    <p>Every boss" not in html:
    html = re.sub(r"(<h1>CBosses</h1>\s*)<p>[^<]*", r"\1<p>Every boss in the plugin as it is built in game: block models with their own attacks, entrance and death. Drag to turn the camera, scroll or pinch to zoom. Flying bosses flap, the egg really hatches, and deaths shatter into shards. The browser draws rough stand-ins for the block textures; in game every piece is a real Minecraft block.", html, count=1, flags=re.S)
sub('/* Layout: a night-arena stage on the left that stays put, a roster of 24 bosses on the right', '/* Layout: a night-arena stage on the left that stays put, the roster of bosses on the right')

sub('const MOB = { ', 'const MOB = { ZOMBIE: "Zombie", PHANTOM: "Phantom", PILLAGER: "Pillager", ')
sub('detonate: "Detonate", roar: "Roar" };', 'detonate: "Detonate", roar: "Roar", charge: "Charge", slam: "Slam", meteor: "Meteor", sonic_boom: "Sonic boom", skulls: "Skulls", breath: "Breath", spikes: "Spikes", orbs: "Orbs", gifts: "Gifts", sprinkles: "Sprinkles", dive: "Dive", eggs: "Eggs" };')
sub('GUST_EMITTER_LARGE: "#e0fbff", ASH: "#555555", BLOCK: "#8a7a6a" };',
    'GUST_EMITTER_LARGE: "#e0fbff", ASH: "#555555", BLOCK: "#8a7a6a", DRAGON_BREATH: "#d14bff", SCULK_SOUL: "#4ae3e3", SCULK_CHARGE_POP: "#2fd6d6", SONIC_BOOM: "#4ae3e3", NOTE: "#7cff7c", CHERRY_LEAVES: "#ffb0d0", COMPOSTER: "#7bd66a", HAPPY_VILLAGER: "#7bd66a", SNOWFLAKE: "#e8f6ff", DRIPPING_WATER: "#3aa6ff", FALLING_WATER: "#3aa6ff" };')

# "!" in step filters, like the plugin
sub('function matches(only, i) {\n  if (!only || only === "all") return true;', 'function matches(only, i) {\n  if (!only || only === "all") return true;\n  if (only[0] === "!") return !matches(only.slice(1), i);')

# fling: thrown like a burst, tumbling; shatter is handled in tickSteps
sub('    case "spin": return new Mt().makeRotationY((s.deg || 90) * D2R);',
    '    case "fling": { const out = stepMatrix(Object.assign({}, s, { op: "burst", up: 0 }), i), keep = cur.op[i]; cur.op[i] = out.clone().multiply(keep); const down = stepMatrix({ op: "drop" }, i); cur.op[i] = keep; return down.multiply(out); }\n    case "spin": return new Mt().makeRotationY((s.deg || 90) * D2R);')

# flash, shake and shatter
sub('    if (s.op === "light") {',
    '''    if (s.op === "flash") { const i = e.cube, was = cur.block[i]; cur.meshes[i].material = material(s.block || "white_concrete", true, DATA.palette);
      setTimeout(() => { if (cur && cur.meshes[i]) cur.meshes[i].material = material(cur.block[i], cur.lit[i], DATA.palette); }, Math.max(1, s.dur || 3) * 50); continue; }
    if (s.op === "shake") { shakeUntil = Math.max(shakeUntil, now + Math.max(1, s.dur || 10) * 50); shakeAmp = Math.max(shakeAmp, s.amp || 0.06 + 0.025 * cur.H); continue; }
    if (s.op === "shatter") { shatter(e.cube, s, now); continue; }
    if (s.op === "light") {''')
sub('function resetShape() {', '''let shakeUntil = 0, shakeAmp = 0;
const shards = [];
function shatter(i, s, now) {
  const m = displayOp(i, now).clone().multiply(cur.pose[i]), c = center(m), sc = new V(); m.decompose(new V(), new Q(), sc);
  const n = Math.max(1, Math.min(8, s.pieces || 3)), mat = material(cur.block[i], cur.lit[i], DATA.palette);
  for (let k = 0; k < n; k++) {
    if (shards.length > 220) break;
    const g = new THREE.Mesh(GEO, mat); g.matrixAutoUpdate = true;
    const size = Math.max(0.04, Math.cbrt(Math.abs(sc.x * sc.y * sc.z)) * 0.5);
    g.scale.setScalar(size); g.position.set(c.x + (rnd() - 0.5) * 0.2, c.y, c.z + (rnd() - 0.5) * 0.2);
    let dx = c.x, dz = c.z, len = Math.hypot(dx, dz) || 1; if (len < 0.05) { const a = rnd() * 6.28; dx = Math.cos(a); dz = Math.sin(a); len = 1; }
    const p = (s.power || 3) * (0.5 + rnd()), up = (s.up || 2.5) * (0.6 + rnd() * 0.8);
    g.userData = { v: new V(dx / len * p + (rnd() - 0.5) * 2, up * 1.6, dz / len * p + (rnd() - 0.5) * 2), w: new V(rnd() * 8, rnd() * 8, rnd() * 8), born: now, life: 1800 + rnd() * 700 };
    scene.add(g); shards.push(g);
  }
  setOp(i, new Mt().makeTranslation(c.x, c.y, c.z).multiply(new Mt().makeScale(1e-4, 1e-4, 1e-4)).multiply(new Mt().makeTranslation(-c.x, -c.y, -c.z)).multiply(cur.op[i]), 0, now);
}
function tickShards(now, dt) {
  for (let i = shards.length - 1; i >= 0; i--) {
    const g = shards[i], u = g.userData, age = (now - u.born) / u.life;
    if (age >= 1) { scene.remove(g); shards.splice(i, 1); continue; }
    u.v.y -= dt * 22; g.position.addScaledVector(u.v, dt);
    if (g.position.y < g.scale.x * 0.5) { g.position.y = g.scale.x * 0.5; u.v.y = Math.abs(u.v.y) * 0.3; u.v.x *= 0.6; u.v.z *= 0.6; u.w.multiplyScalar(0.6); }
    g.rotation.x += u.w.x * dt; g.rotation.y += u.w.y * dt; g.rotation.z += u.w.z * dt;
    if (age > 0.75) g.scale.setScalar(g.scale.x * 0.9);
  }
}
function resetShape() {''')

# entrance-only shell cubes (the egg) and flying
sub('  const n = model.cubes.length;', '''  const n = model.cubes.length;
  const parentOf = Object.fromEntries(model.bones.map(b => [b.name, b.parent]));
  const shellOf = b => { while (b) { if (b.startsWith("shell")) return true; b = parentOf[b]; } return false; };''')
sub("anim: Array.from({ length: n }, () => null), block:", "anim: Array.from({ length: n }, () => null), shell: model.cubes.map(c => shellOf(c.b)), block:")
sub("  if (walkW > 0.01) layers.push({ anim: r.walk, t: walkT, w: walkW });",
    "  const flies = cur.boss.movement === \"fly\" && r.fly;\n  if (flies) layers.push({ anim: r.fly, t: idleT, w: 1 });\n  else if (walkW > 0.01) layers.push({ anim: r.walk, t: walkT, w: walkW });")
sub("    for (let i = 0; i < cur.meshes.length; i++) cur.meshes[i].matrix.copy(displayOp(i, now)).multiply(cur.pose[i]);",
    """    for (let i = 0; i < cur.meshes.length; i++) {
      cur.meshes[i].matrix.copy(displayOp(i, now)).multiply(cur.pose[i]);
      if (mode === "live" && cur.shell[i]) cur.meshes[i].matrix.makeScale(1e-4, 1e-4, 1e-4);
    }
    const lift = cur.boss.movement === "fly" ? 2.2 : cur.boss.movement === "hover" ? 0.8 : 0;
    cur.group.position.y += ((mode === "live" ? lift : 0) - cur.group.position.y) * Math.min(1, dt * 3);
    if (now < shakeUntil) cur.group.position.set((rnd() - 0.5) * shakeAmp, cur.group.position.y + (rnd() - 0.5) * shakeAmp * 0.5, (rnd() - 0.5) * shakeAmp);
    else { cur.group.position.x = 0; cur.group.position.z = 0; shakeAmp = 0; }""")
sub("  tickFx(now, dt);\n  controls.update();", "  tickFx(now, dt);\n  tickShards(now, dt);\n  controls.update();")

# roster groups and info
sub('const groups = [["Weekly bosses", DATA.bosses.filter(b => !b.season)], ["Seasonal bosses", DATA.bosses.filter(b => b.season)]];',
    'const groups = [["Legends and the finale", DATA.bosses.filter(b => b.kind === "legend")], ["World bosses", DATA.bosses.filter(b => b.kind === "world")], ["Chapter bosses", DATA.bosses.filter(b => b.kind === "chapter")], ["Seasonal bosses", DATA.bosses.filter(b => b.kind === "seasonal")], ["Mini bosses", DATA.bosses.filter(b => b.kind === "mini")], ["Decor", DATA.bosses.filter(b => b.kind === "decor")]];')
sub('${DATA.models[b.id].cubes.length} blocks${b.season ? " · " + nice(b.season) : ""}',
    '${DATA.models[b.id].cubes.length} blocks${b.season ? " · " + nice(b.season) : ""}${b.chapter ? " · chapter " + b.chapter : ""}${b.movement === "fly" ? " · flies" : ""}')
sub('<p class="sub">${boss.title}${boss.season ? " · " + nice(boss.season) + " season" : ""}</p>',
    '<p class="sub">${boss.title}${boss.season ? " · " + nice(boss.season) + " season" : ""}${boss.chapter ? " · after chapter " + boss.chapter : ""}</p>\n    <p>${boss.description}</p>')
sub('<span><b>Mob under it</b>${MOB[boss.entity] || boss.entity}</span>', '<span><b>Mob under it</b>${MOB[boss.entity] || nice(boss.entity.toLowerCase())}</span><span><b>Moves</b>${nice(boss.movement)}</span><span><b>Theme</b>${nice(boss.theme)}</span>')
sub('choose(DATA.models[start] ? start : "gravelord");', 'choose(DATA.models[start] ? start : "the_listener");')

dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs", "viewer.html")
os.makedirs(os.path.dirname(dest), exist_ok=True)
open(dest, "w").write(html)
print("viewer written to", dest, len(html) // 1024, "KB,", len(out), "bosses")
