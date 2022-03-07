#!/usr/bin/env bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

pip_list=$(python3 -m pip list 2> /dev/null)
if ! echo "$pip_list" | grep libtmux -q; then
    tmux display "ERROR: tmux-window-name - Python dependency libtmux not found (Check the README)"
    exit 0
fi

tmux set -g automatic-rename off
tmux set-hook -g 'session-window-changed[8921]' "run-shell "$CURRENT_DIR/scripts/rename_session_windows.py""
