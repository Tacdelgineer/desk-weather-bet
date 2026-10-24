#!/usr/bin/env bash
# usage: tools/done.sh <task-id> <mark: x|⏸|⚠️> "<state lines>" [extra text after mark]
# Marks a PLAN.md task, appends to STATE.md, commits and pushes.
set -euo pipefail
cd "$(dirname "$0")/.."
id="$1"; mark="$2"; note="$3"; extra="${4:-}"
case "$mark" in
  x) new="[x]";;
  ⏸) new="⏸";;
  ⚠️) new="⚠️";;
  *) echo "bad mark"; exit 1;;
esac
python3 - "$id" "$new" "$extra" <<'PY'
import re, sys, pathlib
tid, new, extra = sys.argv[1], sys.argv[2], sys.argv[3]
p = pathlib.Path("PLAN.md"); s = p.read_text()
pat = re.compile(r"^- (\[ \]|\[x\]|⏸[^*\n]*|⚠️[^*\n]*)\s*(\*\*" + re.escape(tid) + r" )", re.M)  # marks may carry a note
m = pat.search(s)
if not m: sys.exit(f"task {tid} not found")
rep = f"- {new}" + (f" {extra}" if extra else "") + " " + m.group(2)
s = s[:m.start()] + rep + s[m.end():]
p.write_text(s)
PY
printf '\n**%s — %s** %s\n%s\n' "$(date -u +%F)" "$id" "($new)" "$note" >> STATE.md
git add -A
git commit -qm "$id: $(echo "$note" | head -1 | cut -c1-60)"
git push -q origin main
