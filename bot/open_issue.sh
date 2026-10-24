#!/usr/bin/env bash
# 7.1 step 3 — open the public "Live picks log" issue as the channel account and post RULES.md's SHA-256 and the
# rules-locked commit as its first comment (GitHub sets comment times server-side; they can't be back-dated).
# Then save the issue number to LIVE_ISSUE (read by bot/live.py), tick 7.1, commit and push. Safe to re-run.
set -euo pipefail
cd "$(dirname "$0")/.."
REPO=Tacdelgineer/desk-weather-bet
who=$(gh api user --jq .login)
[ "$who" = "Tacdelgineer" ] || { echo "gh is logged in as '$who' — run: gh auth login (as Tacdelgineer), or gh auth switch -u Tacdelgineer"; exit 1; }
[ -s LIVE_ISSUE ] && { echo "already open: issue #$(cat LIVE_ISSUE)"; exit 0; }
commit=$(git rev-list -n 1 rules-locked)
sha=$(git show rules-locked:RULES.md | sha256sum | cut -d' ' -f1)
url=$(gh issue create -R "$REPO" --title "Live picks log" --body "Daily picks from bot/live.py for the \$10 live test (REAL MONEY · \$10 TEST). Until GO_LIVE exists the bot runs in DRY_RUN and posts what it *would* order. Rules: RULES.md at tag \`rules-locked\`.")
num=${url##*/}
gh issue comment "$num" -R "$REPO" --body "RULES.md SHA-256: \`$sha\` · commit \`$commit\` (tag \`rules-locked\`). Check: \`git show rules-locked:RULES.md | sha256sum\`"
echo "$num" > LIVE_ISSUE
tools/done.sh 7.1 x "- Issue: $url (first comment: RULES.md SHA-256 $sha, commit $commit). LIVE_ISSUE written; bot/live.py posts daily picks there (only as Tacdelgineer)."
echo "$url"
