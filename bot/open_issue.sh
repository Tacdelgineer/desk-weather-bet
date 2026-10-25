#!/usr/bin/env bash
# 7.1 step 3 — open the public "Live picks log" issue as the channel account. Its first comment holds RULES.md's
# SHA-256 and commit for v1 (tag rules-locked, superseded) and v2 (tag rules-locked-v2, the live rules).
# GitHub sets comment times server-side; they can't be back-dated.
# Then save the issue number to LIVE_ISSUE (read by bot/live.py), tick 7.1, commit and push. Safe to re-run.
set -euo pipefail
cd "$(dirname "$0")/.."
REPO=Tacdelgineer/desk-weather-bet
who=$(gh api user --jq .login)
[ "$who" = "Tacdelgineer" ] || { echo "gh is logged in as '$who' — run: gh auth login (as Tacdelgineer), or gh auth switch -u Tacdelgineer"; exit 1; }
[ -s LIVE_ISSUE ] && { echo "already open: issue #$(cat LIVE_ISSUE)"; exit 0; }
git push -q origin rules-locked rules-locked-v2   # both tags must be public before their hashes are posted
c1=$(git rev-list -n 1 rules-locked); s1=$(git show rules-locked:RULES.md | sha256sum | cut -d' ' -f1)
c2=$(git rev-list -n 1 rules-locked-v2); s2=$(git show rules-locked-v2:RULES.md | sha256sum | cut -d' ' -f1)
url=$(gh issue create -R "$REPO" --title "Live picks log" --body "Daily picks from bot/live.py for the \$10 live test (REAL MONEY · \$10 TEST). Until GO_LIVE exists the bot runs in DRY_RUN and posts what it *would* order. Rules: RULES.md at tag \`rules-locked-v2\`.")
num=${url##*/}
body="**Locked rules**

- v1: tag \`rules-locked\` · commit \`$c1\` · RULES.md SHA-256 \`$s1\` · **superseded — the dry run found a bug, see video/JOURNAL.md**
- v2 (live): tag \`rules-locked-v2\` · commit \`$c2\` · RULES.md SHA-256 \`$s2\`

Check: \`git show rules-locked-v2:RULES.md | sha256sum\`"
gh issue comment "$num" -R "$REPO" --body "$body"
echo "$num" > LIVE_ISSUE
tools/done.sh 7.1 x "- Issue: $url. First comment: v1 (rules-locked, SHA-256 $s1) marked superseded; v2 (rules-locked-v2, SHA-256 $s2, commit $c2). LIVE_ISSUE written; bot/live.py posts daily picks there (only as Tacdelgineer)."
echo "$url"
