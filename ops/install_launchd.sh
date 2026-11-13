#!/bin/bash
# Install the patchland journal LaunchAgent. Copies ops/*.py to ~/.ipe/patchland-ops/ (stable path launchd runs),
# fills the plist, copies to ~/Library/LaunchAgents, bootstrap. Re-runnable.
# Runnable from any directory (paths are relative to this script). Prereqs: ~/Developer/ipe_web_kit (private kit clone), git push access to origin.
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LABEL=com.ipe.patchland.journal
[ "$(TZ=Asia/Seoul date +%z)" = "$(date +%z)" ] || { echo "Mac timezone is not KST — plist hours would be wrong"; exit 1; }
mkdir -p "$HOME/.ipe/patchland-ops" "$HOME/.ipe/logs" "$HOME/.ipe/queue/patchland"
cp journal_gate.py journal_publish.py "$HOME/.ipe/patchland-ops/"
# Publish clone the publisher commits/pushes from (separate from any dev checkout) + the private kit it needs for build/check.
CLONE="${PATCHLAND_CLONE:-$HOME/ipe/patchland-publish}"
KIT="${IPE_WEB_KIT:-$HOME/Developer/ipe_web_kit}"
[ -d "$KIT/.git" ] || { echo "kit clone not found: $KIT (set IPE_WEB_KIT)"; exit 1; }
[ -d "$CLONE/.git" ] || { mkdir -p "$(dirname "$CLONE")"; git clone https://github.com/blessu76/patchland-rest.git "$CLONE"; }
git -C "$CLONE" pull --rebase --quiet
python3 "$CLONE/scripts/kit_lock.py" sync --kit "$KIT"
sed "s#__HOME__#$HOME#g" $LABEL.plist > "$HOME/Library/LaunchAgents/$LABEL.plist"
plutil -lint "$HOME/Library/LaunchAgents/$LABEL.plist"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/$LABEL.plist"
launchctl list | grep "$LABEL"
