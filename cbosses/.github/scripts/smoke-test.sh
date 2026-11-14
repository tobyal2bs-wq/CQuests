#!/usr/bin/env bash
# Starts a real server with CBosses, runs the admin commands from the console (including the self-test that
# spawns every boss, runs every attack and plays every death) and fails on any error, stack trace or warning.
# Usage: smoke-test.sh <paper|folia> <version|latest>
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
cp build/libs/CBosses-*.jar run/plugins/
cd run
curl -fsSL -o server.jar "$URL"
echo "eula=true" > eula.txt
printf 'online-mode=false\nlevel-type=minecraft\\:flat\ngenerate-structures=false\ndifficulty=normal\nspawn-protection=0\n' > server.properties

BOSSES=$(python3 -c 'import yaml,sys; print(len(yaml.safe_load(open(sys.argv[1]))["bosses"]))' "${CB_ROOT:-$GITHUB_WORKSPACE}/src/main/resources/bosses.yml" 2>/dev/null || grep -cE "^  [a-z_]+:$" "${CB_ROOT:-$GITHUB_WORKSPACE}/src/main/resources/bosses.yml")
ABILITIES=28
# Partner bodies (kind: partner) fight alongside their main boss, so the self-test spawns them with it.
TESTED=$(python3 -c 'import yaml,sys; print(sum(1 for b in yaml.safe_load(open(sys.argv[1]))["bosses"].values() if b.get("kind") != "partner"))' "${CB_ROOT:-$GITHUB_WORKSPACE}/src/main/resources/bosses.yml")
echo "Expecting $BOSSES bosses"

touch console
tail -f console | java -Xmx3G -jar server.jar --nogui > server.log 2>&1 &
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
wait_for "CBosses .* enabled with" 30
for cmd in "cbosses list" "cbosses arena radius main 30" "cbosses arena list" "cbosses schedule" "cbosses season" "cbosses season winter on" "cbosses season winter auto" "cbosses finale" \
           "cbosses selftest" "cbosses reload" "cbosses list" "mossback spawn 0 80 0 world" "mossback list"; do
  echo "$cmd" >> console
  sleep 3
  # The self-test plays every omen, entrance, attack and death at once; it reports by itself after 75 seconds at the latest.
  if [ "$cmd" = "cbosses selftest" ]; then wait_for "Boss self-test:" 120; fi
done
echo "stop" >> console
wait "$SERVER" || true
pkill -f "tail -f console" || true

sed 's/\x1b\[[0-9;]*m//g' server.log > plain.log
echo "----- CBosses lines -----"
grep -i "cbosses" plain.log || true
echo "-------------------------"

grep -q "Enabling CBosses" plain.log || { echo "CBosses did not enable"; exit 1; }
grep -qE "CBosses .* enabled with $BOSSES bosses" plain.log || { echo "Not all $BOSSES bosses loaded"; exit 1; }
grep -qE "Bosses \($BOSSES\)" plain.log || { echo "/cbosses list did not list $BOSSES bosses"; exit 1; }
grep -q "Winterfest is now on" plain.log || { echo "/cbosses season winter on failed"; exit 1; }
ATTACKS=$((TESTED * ABILITIES))
grep -qE "Boss self-test: $TESTED/$TESTED appeared, $ATTACKS attacks ran, $TESTED drawn with [0-9]+ blocks and [0-9]+ hit zones, [0-9]+ animations, $TESTED deaths played" plain.log \
  && ! grep -q "Boss self-test.*Problems" plain.log || { echo "Boss self-test failed"; grep -E "self-test|CBosses" plain.log | tail -30; exit 1; }
grep -E "Boss self-test" plain.log
grep -qE "Reloaded: $BOSSES bosses" plain.log || { echo "/cbosses reload failed"; exit 1; }
grep -q "Friendly Mossbacks: 1" plain.log || { echo "Friendly Mossback spawn failed"; exit 1; }
if grep -E "at com\.cbosses|Error occurred while enabling CBosses|\[CBosses\].*(ERROR|SEVERE)|Exception.*cbosses" plain.log; then
  echo "CBosses logged an error"
  exit 1
fi
if grep -E "WARN\].*\[CBosses\]" plain.log; then
  echo "CBosses logged warnings (see above)"
  exit 1
fi
echo "Smoke test passed on $PROJECT $VERSION"
