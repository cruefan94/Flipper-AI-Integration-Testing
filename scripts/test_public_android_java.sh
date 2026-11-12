#!/usr/bin/env bash
set -euo pipefail
# Fetch the real public Android implementation at a pinned commit, not a moving branch.
SHA="8dfa2c02139f1bc8230f969a3638d30f1f3cb0e9"
URL="https://raw.githubusercontent.com/cruefan94/Flipper-AI-Android-Satellite/$SHA/android_satellite/app/src/main/java/com/flipperai/satellite/SatelliteProtocol.java"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/src/com/flipperai/satellite" "$WORK/classes"
curl --fail --location --silent --show-error --retry 3 "$URL" -o "$WORK/src/com/flipperai/satellite/SatelliteProtocol.java"
test -s "$WORK/src/com/flipperai/satellite/SatelliteProtocol.java"
javac -encoding UTF-8 -d "$WORK/classes" "$WORK/src/com/flipperai/satellite/SatelliteProtocol.java" tests/java/Ai1WireSmoke.java
java -cp "$WORK/classes" Ai1WireSmoke
