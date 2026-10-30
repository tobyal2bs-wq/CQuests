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
for cmd in "cq npc list" "cq quest story_bob" "cq quest side_stephan_1" "cq reload" "cq npc list"; do
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
if grep -E "at com\.cquests|Error occurred while enabling CQuests|\[CQuests\].*(ERROR|SEVERE)" server.log; then
  echo "CQuests logged an error"
  exit 1
fi
if grep -E "WARN\].*\[CQuests\]" server.log; then
  echo "CQuests logged warnings (see above)"
  exit 1
fi
echo "Smoke test passed on $PROJECT $VERSION"
