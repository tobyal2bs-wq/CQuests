#!/usr/bin/env bash
# Starts a real server with the plugin, runs a few admin commands from the console and fails
# if CQuests logs an error or a stack trace. Usage: smoke-test.sh <paper|folia> <version|latest>
set -euo pipefail

PROJECT="$1"
VERSION="$2"
API="https://fill.papermc.io/v3/projects/$PROJECT"

if [ "$VERSION" = "latest" ]; then
  VERSION=$(curl -fsSL "$API" | python3 -c '
import json, sys
versions = json.load(sys.stdin)["versions"]
flat = [v for group in versions.values() for v in group] if isinstance(versions, dict) else versions
print(next(v for v in flat if "-" not in v))')
fi
echo "Testing $PROJECT $VERSION"
URL=$(curl -fsSL "$API/versions/$VERSION/builds/latest" | python3 -c 'import json, sys; print(json.load(sys.stdin)["downloads"]["server:default"]["url"])')

mkdir -p run/plugins
cp build/libs/CQuests-*.jar run/plugins/
cd run
curl -fsSL -o server.jar "$URL"
echo "eula=true" > eula.txt
printf 'online-mode=false\nlevel-type=minecraft\\:flat\ngenerate-structures=false\n' > server.properties

# A saved player, so backup and restore have something real to work with.
mkdir -p plugins/CQuests/players
printf 'completed:\n- welcome\n- story_stephan\nside-done:\n  stephan: 3\nstarted: 1\n' > plugins/CQuests/players/00000000-0000-0000-0000-000000000001.yml

touch console
tail -f console | java -Xmx2G -jar server.jar --nogui > server.log 2>&1 &
SERVER=$!

wait_for() {
  for _ in $(seq 1 "$2"); do
    grep -q "$1" server.log && return 0
    kill -0 "$SERVER" 2>/dev/null || { cat server.log; echo "Server died"; exit 1; }
    sleep 1
  done
  cat server.log
  echo "Timed out waiting for: $1"
  exit 1
}

wait_for "Done (" 300

# On Paper 1.21.4 a test player joins and plays the start of the story.
if [ "$PROJECT" = "paper" ] && [ "$VERSION" = "1.21.4" ]; then
  BOT_DIR=$(mktemp -d)
  cp "$GITHUB_WORKSPACE/.github/scripts/bot.js" "$BOT_DIR/"
  (cd "$BOT_DIR" && npm install --silent --no-audit --no-fund mineflayer@4 > /dev/null)
  # The last quest of chapter 1 and of the whole story, read from quests.yml.
  read -r CHAPTER_ONE_END STORY_END < <(python3 - "$GITHUB_WORKSPACE/src/main/resources/quests.yml" <<'PY'
import re, sys
current, chapters = None, []
for line in open(sys.argv[1], encoding="utf-8"):
    m = re.match(r"^  (story_\w+):", line)
    if m:
        current = m.group(1)
    m = re.match(r"^    chapter: (\d+)", line)
    if m and current:
        chapters.append((current, int(m.group(1))))
print([q for q, c in chapters if c == 1][-1], chapters[-1][0])
PY
)
  echo "Chapter 1 ends with $CHAPTER_ONE_END, the story ends with $STORY_END"
  CHAPTER_ONE_END="$CHAPTER_ONE_END" STORY_END="$STORY_END" MC_VERSION="$VERSION" node "$BOT_DIR/bot.js" > bot.log 2>&1 &
  BOT=$!
  wait_for "CQBot joined the game" 60
  echo "op CQBot" >> console
  if ! wait "$BOT"; then
    cat bot.log
    echo "The test player failed"
    exit 1
  fi
  cat bot.log
  sleep 2
  grep -q "\[Chapter 1: The Wanderers' Camp\]" server.log || { echo "Chapter 1 achievement was not given"; exit 1; }
  grep -q "\[Finished the Journey\]" server.log || { echo "Ending achievement was not given"; exit 1; }
fi
for cmd in "cq npc list" "cq quest story_bob" "cq quest side_stephan_1" "cq reload" "cq npc list" \
           "cq backup" "cq backups" "cq restore latest 00000000-0000-0000-0000-000000000001"; do
  echo "$cmd" >> console
  sleep 4
done
echo "stop" >> console
wait "$SERVER" || true
pkill -f "tail -f console" || true

echo "----- CQuests lines -----"
grep -i "cquests" server.log || true
echo "-------------------------"

grep -q "Enabling CQuests" server.log || { echo "CQuests did not enable"; exit 1; }
grep -q "Auto-placed" server.log || { echo "NPCs were not placed"; exit 1; }
grep -q "Registered 6 achievements" server.log || { echo "Achievements were not registered"; exit 1; }
grep -qE "Backed up [0-9]+ players? to" server.log || { echo "Backup did not run"; exit 1; }
grep -q "Restored 1 player" server.log || { echo "Restore did not run"; exit 1; }
ls plugins/CQuests/backups/*shutdown.zip > /dev/null || { echo "No backup on shutdown"; exit 1; }
if grep -E "at com\.cquests|Error occurred while enabling CQuests|\[CQuests\].*(ERROR|SEVERE)" server.log; then
  echo "CQuests logged an error"
  exit 1
fi
if grep -E "WARN\].*\[CQuests\]" server.log; then
  echo "CQuests logged warnings (see above)"
  exit 1
fi
echo "Smoke test passed on $PROJECT $VERSION"
