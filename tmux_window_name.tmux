#!/usr/bin/env bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# source "$CURRENT_DIR/scripts/helpers.sh"

# TODO: install requirements
tmux set -g automatic-rename off

# TODO: other hooks?
# TODO: enable pane-events (see man tmux)
tmux set-hook -g 'session-window-changed[8921]' "run-shell "$CURRENT_DIR/scripts/rename_session_windows.py""
