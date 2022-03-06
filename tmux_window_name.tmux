#!/usr/bin/env bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ "$(pip3 list | grep libtmux)" = "" ]; then
    tmux display "ERROR: tmux-window-name - Python dependency libtmux not found (Check the README)"
    exit 0
fi

tmux set -g automatic-rename off
tmux set-hook -g 'session-window-changed[8921]' "run-shell "$CURRENT_DIR/scripts/rename_session_windows.py""
