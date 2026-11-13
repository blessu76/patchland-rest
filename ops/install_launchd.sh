#!/bin/bash
# Install the patchland journal LaunchAgent. Copies ops/*.py to ~/.ipe/patchland-ops/ (stable path launchd runs),
# fills the plist, copies to ~/Library/LaunchAgents, bootstrap. Re-runnable.
set -euo pipefail
cd "$(dirname "$0")"
LABEL=com.ipe.patchland.journal
[ "$(TZ=Asia/Seoul date +%z)" = "$(date +%z)" ] || { echo "Mac timezone is not KST — plist hours would be wrong"; exit 1; }
mkdir -p "$HOME/.ipe/patchland-ops" "$HOME/.ipe/logs" "$HOME/.ipe/queue/patchland"
cp journal_gate.py journal_publish.py "$HOME/.ipe/patchland-ops/"
sed "s#__HOME__#$HOME#g" $LABEL.plist > "$HOME/Library/LaunchAgents/$LABEL.plist"
plutil -lint "$HOME/Library/LaunchAgents/$LABEL.plist"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/$LABEL.plist"
launchctl list | grep "$LABEL"
