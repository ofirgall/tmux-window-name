#!/usr/bin/env bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

python3 -m pip install libtmux --user

tmux set -g automatic-rename off
tmux set-hook -g 'session-window-changed[8921]' "run-shell "$CURRENT_DIR/scripts/rename_session_windows.py""
