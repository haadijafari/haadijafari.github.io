#!/usr/bin/env bash
# Headless Firefox screenshots of the local site at phone, tablet and desktop sizes.
# Usage: tools/screens.sh <label> [#anchor] [pixel offset below the anchor]
# Anchor shots load tools/frame.html, which scrolls the page in an iframe before capture.
# SIZES="390x844 1280x800" limits the sizes.
# Output: ~/snap/firefox/common/claude-prof/shots/<label>[-anchor]-<w>x<h>.png
# (snap Firefox can only write under ~/snap/firefox/common)
set -euo pipefail

label=${1:?usage: tools/screens.sh <label> [#anchor]}
anchor=${2:-}
offset=${3:-0}
root="$(cd "$(dirname "$0")/.." && pwd)"
prof="$HOME/snap/firefox/common/claude-prof"
out="$prof/shots"
port=8765
mkdir -p "$out"

if ! (exec 3<>"/dev/tcp/127.0.0.1/$port") 2>/dev/null; then
  (cd "$root" && nohup python3 -m http.server "$port" >/dev/null 2>&1 &)
  sleep 1
fi

suffix=""
[ -n "$anchor" ] && suffix="-${anchor#\#}"
[ "$offset" != 0 ] && suffix="$suffix+$offset"
[ -f "$root/tools/frame.html" ] || { echo "missing .superpowers/frame.html harness" >&2; exit 1; }
for size in ${SIZES:-360x800 390x844 430x932 844x390 768x1024 1280x800}; do
  w=${size%x*}; h=${size#*x}
  file="$out/$label$suffix-$size.png"
  url="http://localhost:$port/"
  # Anchors go through a same-origin iframe harness that scrolls before the capture.
  [ -n "$anchor" ] && url="http://localhost:$port/tools/frame.html?w=$w&h=$h&a=${anchor#\#}&o=${offset:-0}"
  timeout 60 firefox --headless --no-remote --profile "$prof" --window-size="$w,$h" \
    --screenshot "$file" "$url" >/dev/null 2>&1 || true
  [ -f "$file" ] && echo "$file" || echo "MISSING $file"
done
