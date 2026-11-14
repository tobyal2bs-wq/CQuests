"""Writes the text: section of src/main/resources/messages.yml from every T.t("key", "fallback") in the code,
so the file always lists every line the plugin can send. Run from the repo root."""
import os, re
MARK = "# ---------------------------------------------------------------- every other line"
HEAD = """# ---------------------------------------------------------------- every other line
# Every other line CBosses shows: command replies, the menu, action bars, titles and the defeat broadcast.
# Change any of them. Words in <angle brackets> that are not colours are filled in by the plugin
# (for example <boss>, <player>, <arena>, <label> for the command name). Boss names, titles and
# descriptions are in bosses.yml.
text:"""
call = re.compile(r'T\.t\("([a-z0-9.\-]+)",\s*"((?:[^"\\]|\\.)*)"')
found = {}
for root, _, files in os.walk("src/main/java"):
    for fn in sorted(files):
        if fn.endswith(".java"):
            for k, v in call.findall(open(os.path.join(root, fn)).read()):
                found.setdefault(k, v)
help = open("src/main/java/com/cbosses/command/BossCommand.java").read()
for k, v in re.findall(r'\{"([a-z]+)", "((?:[^"\\]|\\.)*)"\}', help):
    found["command.help." + k] = " <yellow>" + v
p = "src/main/resources/messages.yml"
s = open(p).read()
if MARK in s: s = s[:s.index(MARK)].rstrip() + "\n"
tree = {}
for k in sorted(found):
    node = tree
    parts = k.split(".")
    for part in parts[:-1]: node = node.setdefault(part, {})
    node[parts[-1]] = found[k]
names = {"command": "commands", "fight": "fights, arenas and rewards", "menu": "the boss menu", "chapter": "chapter bosses", "season": "seasons", "finale": "the finale"}
out = [s.rstrip(), "", HEAD]
def emit(node, depth):
    for k, v in node.items():
        pad = "  " * depth
        if isinstance(v, dict):
            if depth == 1: out.append(f"{pad}# {names.get(k, k)}")
            out.append(f"{pad}{k}:")
            emit(v, depth + 1)
        else:
            out.append(f'{pad}{k}: "{v}"')
emit(tree, 1)
open(p, "w").write("\n".join(out) + "\n")
print(len(found), "lines in messages.yml text:")
