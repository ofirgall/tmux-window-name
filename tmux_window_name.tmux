#!/usr/bin/env bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if command -v uv >/dev/null 2>&1; then
    LAUNCHER="uv run --script"
else
    LAUNCHER="python3"
    LIBTMUX_AVAILABLE=$(python3 -c "import importlib.util; print(importlib.util.find_spec('libtmux') is not None)" 2>/dev/null)
    if [ "$LIBTMUX_AVAILABLE" = "False" ]; then
        tmux display "ERROR: tmux-window-name - Python dependency libtmux not found (Check the README)"
        exit 0
    fi
fi
export TMUX_WINDOW_NAME_LAUNCHER="$LAUNCHER"

tmux set -g automatic-rename on # Set automatic-rename on to make #{automatic-rename} be on when a new window is been open without a name
tmux set-hook -g 'after-new-window[8921]' 'set -wF @tmux_window_name_enabled \#\{automatic-rename\} ; set -w automatic-rename off'
tmux set-hook -g 'after-select-window[8921]' "run-shell -b \"$LAUNCHER $CURRENT_DIR/scripts/rename_session_windows.py\""

############################################################################################
### Hacks for preserving users custom window names, read more at enable_user_rename_hook ###
############################################################################################

$LAUNCHER "$CURRENT_DIR"/scripts/rename_session_windows.py --enable_rename_hook

# Disabling rename hooks when tmux-ressurect restores the sessions
tmux set -g @resurrect-hook-pre-restore-all "$LAUNCHER $CURRENT_DIR/scripts/rename_session_windows.py --disable_rename_hook"
tmux set -g @resurrect-hook-post-restore-all "$LAUNCHER $CURRENT_DIR/scripts/rename_session_windows.py --post_restore"
