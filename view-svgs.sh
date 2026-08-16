#!/bin/bash
set -euo pipefail

dir="${1:-out}"

if [ ! -d "$dir" ]; then
  echo "Directory not found: $dir" >&2
  exit 1
fi

shopt -s nullglob
files=("$dir"/*.svg)
shopt -u nullglob

if [ ${#files[@]} -eq 0 ]; then
  echo "No SVG files found in: $dir" >&2
  exit 1
fi

browser_app="${SVG_APP:-}"

if [ -z "$browser_app" ]; then
  browser_app="$(python3 - <<'PY'
from pathlib import Path
import plistlib

plist = Path.home() / 'Library/Preferences/com.apple.LaunchServices/com.apple.launchservices.secure.plist'
if not plist.exists():
    raise SystemExit(1)

data = plistlib.loads(plist.read_bytes())
for h in data.get('LSHandlers', []):
    if h.get('LSHandlerURLScheme') in ('http', 'https') and h.get('LSHandlerRoleAll'):
        bundle = h['LSHandlerRoleAll']
        name = bundle.split('.')[-1]
        print(name[0].upper() + name[1:])
        raise SystemExit(0)
raise SystemExit(1)
PY
)"
fi

for f in "${files[@]}"; do
  abs="$(python3 - <<'PY' "$f"
from pathlib import Path
import sys
print(Path(sys.argv[1]).resolve())
PY
)"
  if [ -n "$browser_app" ]; then
    open -a "$browser_app" "file://$abs"
  else
    open "file://$abs"
  fi
done
