"""One-off refactor: moves every chat, action bar, title and menu text that was written into the Java code into
messages.yml (section text:), so server owners can change all of it. A message built from pieces becomes one
line with named placeholders, e.g.  "<red>No arena " + Text.escape(id)  ->  text.no-arena: "<red>No arena <id>".
Run from the repo root. Safe to run again: calls already going through T.t(...) are left alone."""
import os, re, sys, json

SRC = sys.argv[1] if len(sys.argv) > 1 else "src/main/java/com/cbosses"
TPKG = sys.argv[2] if len(sys.argv) > 2 else "com.cbosses"
KEYS = sys.argv[3] if len(sys.argv) > 3 else "build/text-keys.json"
CALLS = ["plugin.send(", "Text.mm("]


def find_close(s, i):
    """s[i] == '(' ; index of the matching ')'."""
    depth, k = 0, i
    while k < len(s):
        ch = s[k]
        if ch == '"':
            k += 1
            while s[k] != '"':
                if s[k] == '\\': k += 1
                k += 1
        elif ch == "'":
            k += 1
            while s[k] != "'":
                if s[k] == '\\': k += 1
                k += 1
        elif ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 0: return k
        k += 1
    raise ValueError("unbalanced")


def split_top(expr, sep):
    """Split at top-level occurrences of a one-character separator."""
    out, depth, cur, k = [], 0, [], 0
    while k < len(expr):
        ch = expr[k]
        if ch == '"':
            j = k + 1
            while expr[j] != '"':
                if expr[j] == '\\': j += 1
                j += 1
            cur.append(expr[k:j + 1]); k = j + 1; continue
        if ch == "'":
            j = k + 1
            while expr[j] != "'":
                if expr[j] == '\\': j += 1
                j += 1
            cur.append(expr[k:j + 1]); k = j + 1; continue
        if ch in "([{": depth += 1
        if ch in ")]}": depth -= 1
        if ch == sep and depth == 0:
            out.append("".join(cur)); cur = []
        else:
            cur.append(ch)
        k += 1
    out.append("".join(cur))
    return out


def is_lit(t):
    t = t.strip()
    return len(t) >= 2 and t[0] == '"' and t[-1] == '"' and '"' not in t[1:-1].replace('\\"', '')


def lit_body(t):
    return t.strip()[1:-1]


def unescape(b):
    return bytes(b, "utf-8").decode("unicode_escape").encode("latin-1").decode("utf-8") if "\\" in b else b


def ph_name(expr, used):
    e = expr.strip()
    e = re.sub(r"^Text\.escape\((.*)\)$", r"\1", e)
    e = re.sub(r"^String\.valueOf\((.*)\)$", r"\1", e)
    specials = [(r"world", "world"), (r"def\.name\(\)|\.def\.name\(\)", "boss"), (r"\.title\(\)", "title"), (r"label$", "label"), (r"getName\(\)", "player"),
                (r"\.id$", "arena"), (r"describe\(\)", "border"), (r"String\.format", "amount"), (r"defs\.size\(\)|defs\(\)\.size\(\)", "count"),
                (r"args\[1\]", "input"), (r"args\[2\]", "input2"), (r"keySet", "list"), (r"ids\(\)", "list"), (r"where\(", "where"), (r"nextText", "time"),
                (r"reason", "reason"), (r"place", "place"), (r"radius", "radius")]
    name = None
    for pat, n in specials:
        if re.search(pat, e): name = n; break
    if not name:
        ids = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", e)
        name = (ids[-1] if ids else "value").lower()
        if name in ("get", "tostring", "valueof"): name = "value"
    base, k = name, 2
    while name in used: name = f"{base}{k}"; k += 1
    used.add(name)
    return name


def slug(text, taken, prefix):
    plain = re.sub(r"<[^>]*>", " ", text)
    words = re.findall(r"[A-Za-z0-9]+", plain.lower())[:5]
    s = "-".join(words) or "line"
    key = f"{prefix}.{s}"
    k = 2
    while key in taken: key = f"{prefix}.{s}-{k}"; k += 1
    return key


def main():
    entries = {}  # key -> (default text, file)
    by_template = {}
    total = 0
    for root, _, files in os.walk(SRC):
        for fn in files:
            if not fn.endswith(".java") or fn in ("T.java",): continue
            path = os.path.join(root, fn)
            s = open(path).read()
            prefix = {"BossService": "fight", "BossCommand": "command", "BossMenu": "menu", "ChapterBosses": "chapter", "Cinematics": "fight",
                      "Abilities": "fight", "Seasons": "season", "CBossesPlugin": "plugin", "Finale": "finale"}.get(fn[:-5], re.sub(r"(?<!^)(?=[A-Z])", "-", fn[:-5]).lower())
            out, i, changed = [], 0, 0
            while True:
                hits = [(s.find(c, i), c) for c in CALLS]
                hits = [(p, c) for p, c in hits if p >= 0]
                if not hits: out.append(s[i:]); break
                p, c = min(hits)
                # skip definitions and lookalikes
                if c == "plugin.send(" and s[p - 1:p].isalnum():
                    out.append(s[i:p + len(c)]); i = p + len(c); continue
                op = p + len(c) - 1
                cl = find_close(s, op)
                inner = s[op + 1:cl]
                args = split_top(inner, ",")
                if c == "plugin.send(":
                    if len(args) < 2: out.append(s[i:cl + 1]); i = cl + 1; continue
                    head = ",".join(args[:-1]) + ","
                    expr = args[-1]
                else:
                    if len(args) != 1: out.append(s[i:cl + 1]); i = cl + 1; continue
                    head, expr = "", args[0]
                lead = expr[:len(expr) - len(expr.lstrip())]
                e = expr.strip()
                if "T.t(" in e or "msg(" in e or len(split_top(e, "?")) > 1:
                    out.append(s[i:cl + 1]); i = cl + 1; continue
                terms = split_top(e, "+")
                lits = [t for t in terms if is_lit(t)]
                if not lits or not any(re.search(r"[A-Za-z]{2,}", re.sub(r"<[^>]*>", "", lit_body(t))) for t in lits):
                    out.append(s[i:cl + 1]); i = cl + 1; continue
                used, tpl, params, seen = set(), [], [], {}
                for t in terms:
                    if is_lit(t): tpl.append(lit_body(t))
                    else:
                        x = t.strip()
                        if x not in seen:
                            seen[x] = ph_name(t, used)
                            params.append((seen[x], x))
                        tpl.append(f"<{seen[x]}>")
                template = "".join(tpl)
                if template in by_template: key = by_template[template]
                else:
                    key = slug(unescape(template), entries, prefix)
                    by_template[template] = key
                    entries[key] = (unescape(template), fn)
                call = f'T.t("{key}", "{template}"' + "".join(f', "{n}", {x}' for n, x in params) + ")"
                out.append(s[i:op + 1] + head + lead + call + ")")
                i = cl + 1
                changed += 1
            if changed:
                txt = "".join(out)
                if f"import {TPKG}.T;" not in txt and f"package {TPKG};" not in txt:
                    txt = re.sub(r"(package [^;]+;\n)", r"\1\nimport " + TPKG + r".T;\n", txt, count=1)
                open(path, "w").write(txt)
                total += changed
                print(f"{fn}: {changed}")
    json.dump(entries, open(KEYS, "w"), indent=1, ensure_ascii=False)
    print(total, "texts,", len(entries), "keys")


if __name__ == "__main__":
    main()
